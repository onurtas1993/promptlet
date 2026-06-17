from PySide6.QtCore import QObject

from promptlet_client.controller.chat_controller import ChatController
from promptlet_client.controller.chat_history_controller import ChatHistoryController
from promptlet_client.controller.settings_controller import SettingsController
from promptlet_client.provider.provider_factory import ProviderFactory
from promptlet_client.repository.history_repository import HistoryRepository
from promptlet_client.repository.settings_repository import SettingsRepository
from promptlet_client.view.application_view import ApplicationView
from promptlet_client.view.settings_view import SettingsView


class ApplicationManager(QObject):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.settings_repository = SettingsRepository()
        self.history_repository = HistoryRepository()

        self.application_view = ApplicationView()
        self.settings_view = SettingsView(parent=self.application_view)

        self.settings_controller = SettingsController(
            settings_view=self.settings_view,
            settings_repository=self.settings_repository,
        )

        self.chat_history_controller = ChatHistoryController(
            chat_history_view=self.application_view.chat_history_view,
            history_repository=self.history_repository,
        )

        self.chat_controller = ChatController(
            chat_view=self.application_view.chat_view,
            session=self.chat_history_controller.active_chat.session,
            settings=self.settings_controller.settings,
            provider=ProviderFactory.create(self.settings_controller.settings.provider),
        )

        self._connect_controllers()
        self.chat_controller.set_session(self.chat_history_controller.active_chat.session)

    def _connect_controllers(self) -> None:
        self.chat_controller.settings_requested.connect(
            self.settings_controller.open_settings
        )
        self.settings_controller.settings_changed.connect(
            self.chat_controller.update_settings
        )
        self.chat_history_controller.chat_selected.connect(self.chat_controller.set_session)
        self.chat_controller.message_history_changed.connect(
            self.chat_history_controller.save_active_chat
        )
        self.application_view.closing.connect(self.settings_controller.save_current_settings)
        self.application_view.closing.connect(self.chat_history_controller.save_all)

    def show(self) -> None:
        self.application_view.show()
