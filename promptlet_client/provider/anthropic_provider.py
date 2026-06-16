import requests

from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.provider.base_provider import BaseProvider


class AnthropicProvider(BaseProvider):
    def send_message(
        self,
        settings: ChatbotSettings,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        response = requests.post(
            f"{settings.base_url.rstrip('/')}/v1/messages",
            headers={
                "x-api-key": settings.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.model,
                "max_tokens": settings.max_tokens,
                "system": system_prompt,
                "messages": messages,
            },
            timeout=(5, 30),
        )

        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()
