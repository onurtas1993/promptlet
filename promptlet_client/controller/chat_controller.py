from PySide6.QtCore import QObject, QThread, Signal, Slot

from promptlet_client.model.chat_session import ChatSession
from promptlet_client.model.chat_message import ChatMessage
from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.provider.base_provider import BaseProvider
from promptlet_client.provider.provider_factory import ProviderFactory
from promptlet_client.service.prompt_service import system_prompt
from promptlet_client.view.chat_view import ChatView
from promptlet_client.worker.chat_request_worker import ChatRequestWorker
from promptlet_client.worker.askthebook_worker import AskTheBookWorker


class ChatController(QObject):
    settings_requested = Signal()
    message_history_changed = Signal()
    closing = Signal()
    busy_changed = Signal(bool)

    def __init__(
        self,
        chat_view: ChatView,
        session: ChatSession,
        settings: ChatbotSettings,
        provider: BaseProvider,
    ) -> None:
        super().__init__()

        self.chat_view = chat_view
        self.session = session
        self.settings = settings
        self.provider = provider

        self._thread: QThread | None = None
        self._worker: ChatRequestWorker | AskTheBookWorker | None = None
        self._documents: list[dict] = []
        self._request_document: dict | None = None

        self._connect_signals()
        self._configure_session()

    def _configure_session(self) -> None:
        self.chat_view.configure_documents(self.settings.askthebook_enabled, self.session.chat_type)
        documents = list(self._documents)
        selected = self.session.document
        if selected and not any(item["document_id"] == selected["document_id"] for item in documents):
            documents.append(selected)
        self.chat_view.set_documents(documents, selected["document_id"] if selected else None)

    @Slot(object)
    def select_document(self, document) -> None:
        if not self.busy and self.session.chat_type == "pdf":
            self.session.document = document
            self.message_history_changed.emit()

    @property
    def busy(self) -> bool:
        return self._thread is not None

    def _connect_signals(self) -> None:
        self.chat_view.settings_requested.connect(self.settings_requested.emit)
        self.chat_view.reset_requested.connect(self.reset_chat)
        self.chat_view.question_submitted.connect(self.ask)
        self.chat_view.closing.connect(self.closing.emit)
        self.chat_view.documents_requested.connect(self.refresh_documents)
        self.chat_view.pdf_selected.connect(self.attach_pdf)
        self.chat_view.document_changed.connect(self.select_document)

    @Slot(object)
    def set_session(self, session: ChatSession) -> None:
        if self._thread is not None:
            return

        self.session = session
        self._configure_session()
        self.chat_view.render_session(self.session)
        self.chat_view.question_input.setFocus()

    @Slot(ChatbotSettings)
    def update_settings(self, settings: ChatbotSettings) -> None:
        if (settings.askthebook_url != self.settings.askthebook_url
                or settings.askthebook_enabled != self.settings.askthebook_enabled):
            self._documents = []
            if settings.askthebook_url != self.settings.askthebook_url:
                self.session.document = None
        self.settings = settings
        self._configure_session()
        self.provider = ProviderFactory.create(settings.provider)
        self.add_system_message("Settings saved.", "#2eff9b")

    def add_system_message(self, message: str, color: str = "#ff5555") -> None:
        self.chat_view.add_chat_line(
            "System",
            message,
            color,
        )

    def ask(self, question: str) -> None:
        if self._thread is not None:
            return

        document = None
        if self.session.chat_type == "pdf":
            if not self.settings.askthebook_enabled:
                self.add_system_message("Enable AskTheBook in Settings to use this PDF chat.")
                return
            document = self.session.document
            if not document:
                self.add_system_message("Attach a PDF or select a prepared document before asking a question.")
                return
        if not document and self.settings.provider == "anthropic" and not self.settings.api_key.strip():
            self.add_system_message(
                "API key is empty. Open Settings and enter your API key.",
                "#ff5555",
            )
            return

        if not document and not self.settings.model.strip():
            self.add_system_message("Open Settings and enter the exact model ID to use.")
            return

        self.chat_view.clear_question()

        self.session.add_user_message(question, document=document)
        self.chat_view.add_chat_line(
            "User",
            question,
            "#00bfff",
            is_user=True,
            metadata=self.session.messages[-1],
        )

        self.message_history_changed.emit()
        self._request_document = document
        if document:
            self._run_worker(
                AskTheBookWorker(self.settings.askthebook_url, "ask", document_id=document["document_id"], question=question, model=self.settings.askthebook_model),
                self._handle_document_answer,
                "AskTheBook is answering; each question is independent...",
            )
        else:
            self._start_worker()

    @Slot()
    def refresh_documents(self) -> None:
        if self.busy or not self.settings.askthebook_enabled or self.session.chat_type != "pdf":
            return
        self._run_worker(AskTheBookWorker(self.settings.askthebook_url), self._handle_documents, "Loading prepared documents...")

    @Slot(str)
    def attach_pdf(self, filename: str) -> None:
        if self.busy or not self.settings.askthebook_enabled or self.session.chat_type != "pdf":
            return
        self._run_worker(
            AskTheBookWorker(self.settings.askthebook_url, "upload", filename=filename),
            self._handle_upload,
            "Uploading and preparing PDF in AskTheBook. This may take several minutes...",
        )

    @Slot(object)
    def _handle_documents(self, documents: list[dict]) -> None:
        selected = self.chat_view.selected_document()
        self._documents = documents
        self.chat_view.set_documents(documents, selected["document_id"] if selected else None)
        self.session.document = self.chat_view.selected_document()
        self.message_history_changed.emit()
        if not documents:
            self.add_system_message("No prepared documents. Use Attach PDF to upload one.", "#aaaaaa")

    @Slot(object)
    def _handle_upload(self, document: dict) -> None:
        self._documents = [item for item in self._documents if item["document_id"] != document["document_id"]]
        self._documents.append(document)
        self.chat_view.set_documents(self._documents, document["document_id"])
        self.session.document = document
        self.message_history_changed.emit()

    @Slot(object)
    def _handle_document_answer(self, result: dict) -> None:
        message = ChatMessage(
            role="assistant", content=result["answer"], document=self._request_document,
            sources=result.get("sources", []), warnings=result.get("warnings", []),
            response_metadata={key: result.get(key) for key in ("model_requested", "model_returned", "finish_reason", "usage")},
        )
        self.session.messages.append(message)
        self.message_history_changed.emit()
        self.chat_view.add_chat_line("Assistant", message.content, "#21f39b", metadata=message)

    def _start_worker(self) -> None:
        worker = ChatRequestWorker(
            provider=self.provider,
            settings=self.settings,
            system_prompt=system_prompt(self.settings.attributes),
            messages=self.session.to_payload(),
        )
        self._run_worker(worker, self._handle_answer, "Assistant is thinking...")

    def _run_worker(self, worker, on_result, status: str) -> None:
        self._thread = QThread()
        self._worker = worker
        self.chat_view.set_waiting(True)
        self.chat_view.status_label.setText(status)
        self.busy_changed.emit(True)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(on_result)
        self._worker.failed.connect(self._handle_error)
        self._worker.completed.connect(self._thread.quit)
        self._worker.completed.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._request_finished)

        self._thread.start()

    @Slot(str)
    def _handle_answer(self, answer: str) -> None:
        self.session.add_assistant_message(answer)
        self.message_history_changed.emit()
        self.chat_view.add_chat_line(
            "Assistant",
            answer,
            "#21f39b",
            is_user=False,
        )

    @Slot(str)
    def _handle_error(self, error: str) -> None:
        self.add_system_message(error, "#ff5555")

    @Slot()
    def _request_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._request_document = None
        self.chat_view.set_waiting(False)
        self.busy_changed.emit(False)
        self.chat_view.question_input.setFocus()

    def reset_chat(self) -> None:
        if self._thread is not None:
            return

        self.session.clear()
        self.message_history_changed.emit()
        self.chat_view.clear_chat()
