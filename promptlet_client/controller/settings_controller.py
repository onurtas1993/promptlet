from PySide6.QtCore import QObject, QThread, Signal, Slot

from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.repository.settings_repository import SettingsRepository
from promptlet_client.view.settings_view import SettingsView
from promptlet_client.worker.askthebook_worker import AskTheBookWorker


class SettingsController(QObject):
    settings_changed = Signal(ChatbotSettings)

    def __init__(
        self,
        settings_view: SettingsView,
        settings_repository: SettingsRepository,
    ) -> None:
        super().__init__()

        self.settings_view = settings_view
        self.settings_repository = settings_repository
        self.settings: ChatbotSettings = self.settings_repository.load()
        self._thread: QThread | None = None
        self._worker: AskTheBookWorker | None = None

        self._connect_signals()
        self.settings_view.set_settings(self.settings)

    def _connect_signals(self) -> None:
        self.settings_view.settings_saved.connect(self.save_settings)
        self.settings_view.documents_requested.connect(self.refresh_documents)

    @property
    def busy(self) -> bool:
        return self._thread is not None

    @Slot(str)
    def refresh_documents(self, base_url: str) -> None:
        if self.busy or not self.settings_view.current_settings().askthebook_enabled:
            return
        self.settings_view.set_documents_busy(True)
        self._thread = QThread()
        self._worker = AskTheBookWorker(base_url)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self.settings_view.show_documents)
        self._worker.failed.connect(self.settings_view.documents_output.setPlainText)
        self._worker.completed.connect(self._thread.quit)
        self._worker.completed.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._documents_finished)
        self._thread.start()

    @Slot()
    def _documents_finished(self) -> None:
        self._thread = None
        self._worker = None
        self.settings_view.set_documents_busy(False)

    def open_settings(self) -> None:
        if not self.busy:
            self.settings_view.set_settings(self.settings)
        self.settings_view.show()
        self.settings_view.raise_()
        self.settings_view.activateWindow()

    @Slot(ChatbotSettings)
    def save_settings(self, settings: ChatbotSettings) -> None:
        self.settings = settings
        self.settings_repository.save(settings)
        self.settings_changed.emit(settings)

    def save_current_settings(self) -> None:
        self.settings_repository.save(self.settings)
