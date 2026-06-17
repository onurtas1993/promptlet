import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from promptlet_client.application_manager import ApplicationManager
from promptlet_client.utils.path_resolver import resource_path


def main() -> None:
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(resource_path("icon.ico"))))

    application_manager = ApplicationManager()
    application_manager.show()

    # Keep the manager alive for the lifetime of the app.
    app.application_manager = application_manager

    sys.exit(app.exec())
