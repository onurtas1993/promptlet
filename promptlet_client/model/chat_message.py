from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str
    content: str

    def to_payload(self) -> dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }
