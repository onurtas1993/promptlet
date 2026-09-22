from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from promptlet_client.model.chat_session import ChatSession


@dataclass
class ChatHistoryItem:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = "New chat"
    session: ChatSession = field(default_factory=ChatSession)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def touch(self) -> None:
        self.updated_at = datetime.now().isoformat(timespec="seconds")

    def refresh_title_from_session(self) -> None:
        for message in self.session.messages:
            if message.role == "user" and message.content.strip():
                title = message.content.strip().replace("\n", " ")
                self.title = title[:40] + ("..." if len(title) > 40 else "")
                return
        self.title = "New chat"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "chat_type": self.session.chat_type,
            "document": self.session.document,
            "messages": [message.to_dict() for message in self.session.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatHistoryItem":
        from promptlet_client.model.chat_message import ChatMessage

        session = ChatSession(
            chat_type=data.get("chat_type", "normal"),
            document=data.get("document"),
            messages=[
                ChatMessage(
                    role=str(message.get("role", "")),
                    content=str(message.get("content", "")),
                    document=message.get("document"),
                    sources=message.get("sources", []),
                    warnings=message.get("warnings", []),
                    response_metadata=message.get("response_metadata", {}),
                )
                for message in data.get("messages", [])
                if isinstance(message, dict)
            ]
        )
        item = cls(
            id=str(data.get("id") or uuid4()),
            title=str(data.get("title") or "New chat"),
            session=session,
            created_at=str(data.get("created_at") or datetime.now().isoformat(timespec="seconds")),
            updated_at=str(data.get("updated_at") or datetime.now().isoformat(timespec="seconds")),
        )
        item.refresh_title_from_session()
        return item
