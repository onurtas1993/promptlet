import json
from dataclasses import asdict
import os
from pathlib import Path

from promptlet_client.model.chatbot_settings import ChatbotSettings


class SettingsRepository:
    APP_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / "Promptlet"
    SETTINGS_FILE = APP_DIR / "settings.json"

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
            max_tokens=int(data.get("max_tokens") or defaults.max_tokens),
            askthebook_url=data.get("askthebook_url") or defaults.askthebook_url,
            askthebook_model=data.get("askthebook_model", ""),
        )

    def save(self, settings: ChatbotSettings) -> None:
        self.APP_DIR.mkdir(parents=True, exist_ok=True)

        data = asdict(settings)

        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
