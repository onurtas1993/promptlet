from PySide6.QtCore import QObject, Signal, Slot

from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.provider.base_provider import BaseProvider


class ChatRequestWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)
    completed = Signal()

    def __init__(
        self,
        provider: BaseProvider,
        settings: ChatbotSettings,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> None:
        super().__init__()
        self.provider = provider
        self.settings = settings
        self.system_prompt = system_prompt
        self.messages = messages

    @Slot()
    def run(self) -> None:
        try:
            answer = self.provider.send_message(
                settings=self.settings,
                system_prompt=self.system_prompt,
                messages=self.messages,
            )
            self.finished.emit(answer)
        except Exception as error:
            self.failed.emit(str(error))
        finally:
            self.completed.emit()
