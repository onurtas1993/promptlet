from dataclasses import dataclass


@dataclass
class ChatbotSettings:
    provider: str = "anthropic"
    attributes: str = "Critical Thinker"
    api_key: str = ""
    base_url: str = "https://api.anthropic.com"
    model: str = "claude-3-5-sonnet-latest"
    max_tokens: int = 4096
