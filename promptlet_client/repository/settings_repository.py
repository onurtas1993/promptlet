import json
from pathlib import Path

from promptlet_client.model.chatbot_settings import ChatbotSettings


class SettingsRepository:
    SETTINGS_FILE = Path(__file__).resolve().parents[2] / "settings.json"

    def load(self) -> ChatbotSettings:
        defaults = ChatbotSettings()

        if not self.SETTINGS_FILE.exists():
            self.save(defaults)
            return defaults

        try:
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return defaults

        return ChatbotSettings(
            provider=data.get("provider") or defaults.provider,
            attributes=data.get("attributes") or defaults.attributes,
            api_key=data.get("api_key") or defaults.api_key,
            base_url=data.get("base_url") or defaults.base_url,
            model=data.get("model") or defaults.model,
            max_tokens=int(data.get("max_tokens")) or defaults.max_tokens
        )

    def save(self, settings: ChatbotSettings) -> None:
        data = {
            "provider": settings.provider,
            "attributes": settings.attributes,
            "api_key": settings.api_key,
            "base_url": settings.base_url,
            "model": settings.model,
            "max_tokens": settings.max_tokens,
        }

        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
