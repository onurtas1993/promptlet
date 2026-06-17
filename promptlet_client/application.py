import sys

from promptlet_client.utils.path_resolver import resource_path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from promptlet_client.controller.chatbot_controller import ChatbotController
from promptlet_client.model.chat_session import ChatSession
from promptlet_client.provider.provider_factory import ProviderFactory
from promptlet_client.repository.settings_repository import SettingsRepository
from promptlet_client.view.chat_view import ChatView
from promptlet_client.view.settings_view import SettingsView


def main() -> None:
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(str(resource_path("icon.ico"))))
    settings_repository = SettingsRepository()
    settings = settings_repository.load()
    session = ChatSession()
    provider = ProviderFactory.create(settings.provider)

    chat_view = ChatView()
    settings_view = SettingsView(parent=chat_view)

    controller = ChatbotController(
        chat_view=chat_view,
        settings_view=settings_view,
        session=session,
        settings_repository=settings_repository,
        provider=provider,
    )

    # Keep the controller alive for the lifetime of the main window.
    chat_view.controller = controller

    chat_view.show()
    sys.exit(app.exec())
