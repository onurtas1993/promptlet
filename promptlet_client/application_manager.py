from PySide6.QtCore import QObject

from promptlet_client.controller.chat_controller import ChatController
from promptlet_client.controller.settings_controller import SettingsController
from promptlet_client.model.chat_session import ChatSession
from promptlet_client.provider.provider_factory import ProviderFactory
from promptlet_client.repository.settings_repository import SettingsRepository
from promptlet_client.view.chat_view import ChatView
from promptlet_client.view.settings_view import SettingsView


class ApplicationManager(QObject):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.settings_repository = SettingsRepository()

        self.chat_view = ChatView()
        self.settings_view = SettingsView(parent=self.chat_view)

        self.settings_controller = SettingsController(
            settings_view=self.settings_view,
            settings_repository=self.settings_repository,
        )

        self.chat_controller = ChatController(
            chat_view=self.chat_view,
            session=ChatSession(),
            settings=self.settings_controller.settings,
            provider=ProviderFactory.create(self.settings_controller.settings.provider),
        )

        self._connect_controllers()

    def _connect_controllers(self) -> None:
        self.chat_controller.settings_requested.connect(
            self.settings_controller.open_settings
        )
        self.chat_controller.closing.connect(
            self.settings_controller.save_current_settings
        )
        self.settings_controller.settings_changed.connect(
            self.chat_controller.update_settings
        )

    def show(self) -> None:
        self.chat_view.show()
