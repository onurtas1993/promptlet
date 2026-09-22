from dataclasses import asdict, dataclass, field


@dataclass
class ChatMessage:
    role: str
    content: str
    document: dict | None = None
    sources: list[dict] = field(default_factory=list)
    warnings: list = field(default_factory=list)
    response_metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_payload(self) -> dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }
