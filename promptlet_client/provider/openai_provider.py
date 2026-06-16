import requests

from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.provider.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    def send_message(
        self,
        settings: ChatbotSettings,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        openai_messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            *messages,
        ]

        response = requests.post(
            f"{settings.base_url.rstrip('/')}/v1/chat/completions",
            headers={
                "authorization": f"Bearer {settings.api_key}",
                "content-type": "application/json",
            },
            json={
                "model": settings.model,
                "messages": openai_messages,
                "max_tokens": settings.max_tokens
            },
            timeout=(5, 30),
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
