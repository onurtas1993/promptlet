from PySide6.QtCore import QObject, Signal, Slot

from promptlet_client.model.chat_history_item import ChatHistoryItem
from promptlet_client.repository.history_repository import HistoryRepository
from promptlet_client.view.chat_history_view import ChatHistoryView


class ChatHistoryController(QObject):
    chat_selected = Signal(object)

    def __init__(
        self,
        chat_history_view: ChatHistoryView,
        history_repository: HistoryRepository,
    ) -> None:
        super().__init__()

        self.chat_history_view = chat_history_view
        self.history_repository = history_repository
        self.chats: list[ChatHistoryItem] = self.history_repository.load()
        self.active_chat_id = self.chats[0].id

        self._connect_signals()
        self._sync_view()

    @property
    def active_chat(self) -> ChatHistoryItem:
        return self._find_chat(self.active_chat_id) or self.chats[0]

    def _connect_signals(self) -> None:
        self.chat_history_view.new_chat_requested.connect(self.create_chat)
        self.chat_history_view.chat_selected.connect(self.select_chat)
        self.chat_history_view.chat_deleted.connect(self.delete_chat)

    def _find_chat(self, chat_id: str) -> ChatHistoryItem | None:
        for chat in self.chats:
            if chat.id == chat_id:
                return chat
        return None

    def _sync_view(self) -> None:
        self.chat_history_view.set_chats(self.chats, self.active_chat_id)

    def _save(self) -> None:
        self.history_repository.save(self.chats)

    @Slot()
    def create_chat(self) -> None:
        chat = ChatHistoryItem()
        self.chats.insert(0, chat)
        self.active_chat_id = chat.id
        self._save()
        self._sync_view()
        self.chat_selected.emit(chat.session)

    @Slot(str)
    def select_chat(self, chat_id: str) -> None:
        chat = self._find_chat(chat_id)
        if chat is None or chat.id == self.active_chat_id:
            return

        self.active_chat_id = chat.id
        self._save()
        self._sync_view()
        self.chat_selected.emit(chat.session)

    @Slot(str)
    def delete_chat(self, chat_id: str) -> None:
        if len(self.chats) == 1:
            self.chats[0] = ChatHistoryItem()
            self.active_chat_id = self.chats[0].id
        else:
            self.chats = [chat for chat in self.chats if chat.id != chat_id]
            if self.active_chat_id == chat_id:
                self.active_chat_id = self.chats[0].id

        self._save()
        self._sync_view()
        self.chat_selected.emit(self.active_chat.session)

    @Slot()
    def save_active_chat(self) -> None:
        self.active_chat.refresh_title_from_session()
        self.active_chat.touch()
        self._save()
        self._sync_view()

    def save_all(self) -> None:
        self.save_active_chat()
