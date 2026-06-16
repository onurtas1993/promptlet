from dataclasses import dataclass, field

from promptlet_client.model.chat_message import ChatMessage


@dataclass
class ChatSession:
    messages: list[ChatMessage] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="assistant", content=content))

    def clear(self) -> None:
        self.messages.clear()

    def to_payload(self) -> list[dict[str, str]]:
        return [message.to_payload() for message in self.messages]
