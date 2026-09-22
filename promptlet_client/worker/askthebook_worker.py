from PySide6.QtCore import QObject, Signal, Slot

from promptlet_client.service.askthebook_service import AskTheBookService


class AskTheBookWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)
    completed = Signal()

    def __init__(self, base_url: str, operation: str = "list", **arguments) -> None:
        super().__init__()
        self.base_url = base_url
        self.operation = operation
        self.arguments = arguments

    @Slot()
    def run(self) -> None:
        try:
            service = AskTheBookService(self.base_url)
            if self.operation == "list":
                result = service.list_documents()
            elif self.operation == "upload":
                result = service.upload_document(**self.arguments)
            elif self.operation == "ask":
                result = service.ask(**self.arguments)
            else:
                raise ValueError(f"Unknown AskTheBook operation: {self.operation}")
            self.finished.emit(result)
        except Exception as error:
            self.failed.emit(str(error))
        finally:
            self.completed.emit()
