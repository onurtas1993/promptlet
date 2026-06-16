from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QWidget

from promptlet_client.view.message_widget import MessageWidget
from promptlet_client.view.ui_loader import load_ui
from promptlet_client.view.styles import (
    APP_STYLESHEET,
    RESET_BUTTON_STYLESHEET,
    SETTINGS_BUTTON_STYLESHEET,
    TITLE_STYLESHEET,
)


class ChatView(QWidget):
    settings_requested = Signal()
    reset_requested = Signal()
    question_submitted = Signal(str)
    closing = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Promptlet")
        self.resize(1200, 800)
        self.setStyleSheet(APP_STYLESHEET)

        self._load_ui()
        self._apply_styles()
        self._connect_signals()
        self.set_waiting(False)

    def _load_ui(self) -> None:
        load_ui(self, "chat_view.ui")

    def _apply_styles(self) -> None:
        self.settings_btn.setStyleSheet(SETTINGS_BUTTON_STYLESHEET)
        self.reset_btn.setStyleSheet(RESET_BUTTON_STYLESHEET)
        self.title_label.setStyleSheet(TITLE_STYLESHEET)
        self.status_label.setStyleSheet("color:#aaaaaa; font-size:14px;")
        self.chat_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _connect_signals(self) -> None:
        self.settings_btn.clicked.connect(self.settings_requested.emit)
        self.reset_btn.clicked.connect(self.reset_requested.emit)
        self.question_input.returnPressed.connect(self._emit_question)

    def _emit_question(self) -> None:
        question = self.question_input.text().strip()
        if question and self.question_input.isEnabled():
            self.question_submitted.emit(question)

    def clear_question(self) -> None:
        self.question_input.clear()

    def set_waiting(self, waiting: bool) -> None:
        self.question_input.setDisabled(waiting)
        self.reset_btn.setDisabled(waiting)
        self.settings_btn.setDisabled(waiting)
        self.status_label.setText("Assistant is thinking..." if waiting else "")

    def add_chat_line(
        self,
        speaker: str,
        text: str,
        color: str,
        is_user: bool = False,
    ) -> None:
        message = MessageWidget(
            speaker=speaker,
            text=text,
            color=color,
            is_user=is_user,
        )

        insert_index = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(insert_index, message)
        QTimer.singleShot(0, self.scroll_to_bottom)

    def scroll_to_bottom(self) -> None:
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_chat(self) -> None:
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def closeEvent(self, event) -> None:
        self.closing.emit()
        super().closeEvent(event)
