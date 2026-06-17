from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from promptlet_client.view.chat_history_view import ChatHistoryView
from promptlet_client.view.chat_view import ChatView
from promptlet_client.view.styles import APP_STYLESHEET
from promptlet_client.view.ui_loader import load_ui


class ApplicationView(QWidget):
    closing = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Promptlet")
        self.resize(1400, 850)
        self.setStyleSheet(APP_STYLESHEET)

        self._load_ui()
        self._add_child_views()

    def _load_ui(self) -> None:
        load_ui(self, "application_view.ui")

    def _add_child_views(self) -> None:
        self.chat_history_view = ChatHistoryView(parent=self)
        self.chat_view = ChatView(parent=self)

        self.main_layout.addWidget(self.chat_history_view)
        self.main_layout.addWidget(self.chat_view, 1)

    def closeEvent(self, event) -> None:
        self.closing.emit()
        super().closeEvent(event)
