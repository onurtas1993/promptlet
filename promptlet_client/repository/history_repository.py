import json
import os
from pathlib import Path

from promptlet_client.model.chat_history_item import ChatHistoryItem


class HistoryRepository:
    APP_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / "Promptlet"
    HISTORY_FILE = APP_DIR / "history.json"

    def load(self) -> list[ChatHistoryItem]:
        if not self.HISTORY_FILE.exists():
            first_chat = ChatHistoryItem()
            self.save([first_chat])
            return [first_chat]

        try:
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return [ChatHistoryItem()]

        items = [
            ChatHistoryItem.from_dict(item)
            for item in data.get("chats", [])
            if isinstance(item, dict)
        ]
        return items or [ChatHistoryItem()]

    def save(self, chats: list[ChatHistoryItem]) -> None:
        self.APP_DIR.mkdir(parents=True, exist_ok=True)
        data = {"chats": [chat.to_dict() for chat in chats]}
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
