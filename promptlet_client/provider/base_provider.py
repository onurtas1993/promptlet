from abc import ABC, abstractmethod

from promptlet_client.model.chatbot_settings import ChatbotSettings


class BaseProvider(ABC):
    @abstractmethod
    def send_message(
        self,
        settings: ChatbotSettings,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        pass
