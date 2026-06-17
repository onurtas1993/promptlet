from PySide6.QtCore import QObject, QThread, Signal, Slot

from promptlet_client.model.chat_session import ChatSession
from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.provider.base_provider import BaseProvider
from promptlet_client.provider.provider_factory import ProviderFactory
from promptlet_client.service.prompt_service import system_prompt
from promptlet_client.view.chat_view import ChatView
from promptlet_client.worker.chat_request_worker import ChatRequestWorker


class ChatController(QObject):
    settings_requested = Signal()
    closing = Signal()

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
        self._worker: ChatRequestWorker | None = None

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.chat_view.settings_requested.connect(self.settings_requested.emit)
        self.chat_view.reset_requested.connect(self.reset_chat)
        self.chat_view.question_submitted.connect(self.ask)
        self.chat_view.closing.connect(self.closing.emit)

    @Slot(ChatbotSettings)
    def update_settings(self, settings: ChatbotSettings) -> None:
        self.settings = settings
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

        if not self.settings.api_key.strip():
            self.add_system_message(
                "API key is empty. Open Settings and enter your API key.",
                "#ff5555",
            )
            return

        self.chat_view.clear_question()

        self.chat_view.add_chat_line(
            "User",
            question,
            "#00bfff",
            is_user=True,
        )

        self.session.add_user_message(question)
        self.chat_view.set_waiting(True)
        self._start_worker()

    def _start_worker(self) -> None:
        self._thread = QThread()
        self._worker = ChatRequestWorker(
            provider=self.provider,
            settings=self.settings,
            system_prompt=system_prompt(self.settings.attributes),
            messages=self.session.to_payload(),
        )

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._handle_answer)
        self._worker.failed.connect(self._handle_error)
        self._worker.completed.connect(self._thread.quit)
        self._worker.completed.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._request_finished)

        self._thread.start()

    @Slot(str)
    def _handle_answer(self, answer: str) -> None:
        self.session.add_assistant_message(answer)
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
        self.chat_view.set_waiting(False)
        self.chat_view.question_input.setFocus()

    def reset_chat(self) -> None:
        if self._thread is not None:
            return

        self.session.clear()
        self.chat_view.clear_chat()
