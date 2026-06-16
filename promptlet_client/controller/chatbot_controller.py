from PySide6.QtCore import QObject, QThread, Slot

from promptlet_client.model.chat_session import ChatSession
from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.repository.settings_repository import SettingsRepository
from promptlet_client.provider.provider_factory import ProviderFactory
from promptlet_client.provider.base_provider import BaseProvider
from promptlet_client.service.prompt_service import system_prompt
from promptlet_client.view.chat_view import ChatView
from promptlet_client.view.settings_view import SettingsView
from promptlet_client.worker.chat_request_worker import ChatRequestWorker


class ChatbotController(QObject):
    def __init__(
        self,
        chat_view: ChatView,
        settings_view: SettingsView,
        session: ChatSession,
        settings_repository: SettingsRepository,
        provider: BaseProvider,
    ) -> None:
        super().__init__()

        self.chat_view = chat_view
        self.settings_view = settings_view
        self.session = session
        self.settings_repository = settings_repository
        self.provider = provider
        self.settings: ChatbotSettings = self.settings_repository.load()

        self._thread: QThread | None = None
        self._worker: ChatRequestWorker | None = None

        self._connect_signals()
        self.settings_view.set_settings(self.settings)

    def _connect_signals(self) -> None:
        self.chat_view.settings_requested.connect(self.open_settings)
        self.chat_view.reset_requested.connect(self.reset_chat)
        self.chat_view.question_submitted.connect(self.ask)
        self.chat_view.closing.connect(self.save_current_settings)
        self.settings_view.settings_saved.connect(self.save_settings)

    def open_settings(self) -> None:
        self.settings_view.set_settings(self.settings)
        self.settings_view.show()
        self.settings_view.raise_()
        self.settings_view.activateWindow()

    def save_settings(self, settings: ChatbotSettings) -> None:
        self.settings = settings
        self.provider = ProviderFactory.create(settings.provider)
        self.settings_repository.save(settings)
        self.chat_view.add_chat_line(
            "System",
            "Settings saved.",
            "#2eff9b",
        )

    def save_current_settings(self) -> None:
        self.settings_repository.save(self.settings)

    def ask(self, question: str) -> None:
        if self._thread is not None:
            return

        if not self.settings.api_key.strip():
            self.chat_view.add_chat_line(
                "System",
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
        self.chat_view.add_chat_line(
            "System",
            error,
            "#ff5555",
        )

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
