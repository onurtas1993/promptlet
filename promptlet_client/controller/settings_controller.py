from PySide6.QtCore import QObject, Signal, Slot

from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.repository.settings_repository import SettingsRepository
from promptlet_client.view.settings_view import SettingsView


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

        self._connect_signals()
        self.settings_view.set_settings(self.settings)

    def _connect_signals(self) -> None:
        self.settings_view.settings_saved.connect(self.save_settings)

    def open_settings(self) -> None:
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
