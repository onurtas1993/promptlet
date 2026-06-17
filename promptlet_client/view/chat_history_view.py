from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidgetItem, QWidget

from promptlet_client.view.styles import (
    DELETE_BUTTON_STYLESHEET,
    HISTORY_STYLESHEET,
    NEW_CHAT_BUTTON_STYLESHEET,
)
from promptlet_client.view.ui_loader import load_ui


class ChatHistoryView(QWidget):
    new_chat_requested = Signal()
    chat_selected = Signal(str)
    chat_deleted = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._load_ui()
        self._apply_styles()
        self._connect_signals()

    def _load_ui(self) -> None:
        load_ui(self, "chat_history_view.ui")

    def _apply_styles(self) -> None:
        self.setStyleSheet(HISTORY_STYLESHEET)
        self.new_chat_btn.setStyleSheet(NEW_CHAT_BUTTON_STYLESHEET)
        self.delete_chat_btn.setStyleSheet(DELETE_BUTTON_STYLESHEET)

    def _connect_signals(self) -> None:
        self.new_chat_btn.clicked.connect(self.new_chat_requested.emit)
        self.delete_chat_btn.clicked.connect(self._emit_delete_requested)
        self.chat_list.currentItemChanged.connect(self._emit_chat_selected)

    def set_chats(self, chats, active_chat_id: str | None) -> None:
        self.chat_list.blockSignals(True)
        self.chat_list.clear()

        selected_row = 0
        for row, chat in enumerate(chats):
            item = QListWidgetItem(chat.title)
            item.setData(256, chat.id)
            self.chat_list.addItem(item)
            if chat.id == active_chat_id:
                selected_row = row

        if self.chat_list.count() > 0:
            self.chat_list.setCurrentRow(selected_row)

        self.chat_list.blockSignals(False)

    def _emit_chat_selected(self, current, previous) -> None:
        if current is None:
            return
        self.chat_selected.emit(current.data(256))

    def _emit_delete_requested(self) -> None:
        item = self.chat_list.currentItem()
        if item is not None:
            self.chat_deleted.emit(item.data(256))
