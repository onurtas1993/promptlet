from dataclasses import dataclass


@dataclass
class ChatbotSettings:
    provider: str = "openai"
    attributes: str = "Critical Thinker"
    api_key: str = ""
    base_url: str = "http://127.0.0.1:1234"
    model: str = ""
    max_tokens: int = 4096
    askthebook_url: str = "http://127.0.0.1:8000"
    askthebook_model: str = ""
