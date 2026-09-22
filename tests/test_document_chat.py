import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from PySide6.QtWidgets import QApplication, QPushButton, QPlainTextEdit

from promptlet_client.controller.chat_controller import ChatController
from promptlet_client.model.chat_history_item import ChatHistoryItem
from promptlet_client.model.chat_session import ChatSession
from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.service.askthebook_service import AskTheBookService
from promptlet_client.view.chat_view import ChatView


DOCUMENT = {"document_id": "doc-1", "name": "example.pdf", "pages": 5, "chunks": 8}
ANSWER = {"document_id": "doc-1", "answer": "Document answer", "sources": [
    {"source": "example.pdf", "page": 3, "text": "Evidence", "rank": 1, "score": 0.8, "chunk_id": "c1", "vector_id": 2}
], "warnings": ["Partial context"], "model_returned": "chosen-model"}


class DocumentChatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def wait_request(self, controller):
        deadline = time.monotonic() + 3
        while controller.busy and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.005)
        self.assertFalse(controller.busy)

    @patch("promptlet_client.service.askthebook_service.requests.post")
    def test_exact_ask_payload_and_optional_model(self, post):
        post.return_value.ok = True
        post.return_value.json.return_value = ANSWER
        service = AskTheBookService("http://localhost:8000")
        service.ask("doc-1", "Question")
        self.assertEqual(post.call_args.kwargs["json"], {"document_id": "doc-1", "question": "Question"})
        service.ask("doc-1", "Question", "chosen-model")
        self.assertEqual(post.call_args.kwargs["json"]["model"], "chosen-model")

    @patch("promptlet_client.service.askthebook_service.requests.post")
    def test_upload_bytes_and_no_retry_on_timeout(self, post):
        def accept(url, **kwargs):
            name, file, content_type = kwargs["files"]["file"]
            self.assertEqual(name, "example.pdf")
            self.assertEqual(file.read(), b"%PDF-test")
            self.assertEqual(content_type, "application/pdf")
            return Mock(ok=True, json=lambda: DOCUMENT)
        post.side_effect = accept
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "example.pdf"
            filename.write_bytes(b"%PDF-test")
            service = AskTheBookService("http://localhost:8000")
            self.assertEqual(service.upload_document(str(filename)), DOCUMENT)
            post.reset_mock()
            post.side_effect = requests.Timeout()
            with self.assertRaisesRegex(RuntimeError, "Processing may still continue"):
                service.upload_document(str(filename))
            self.assertEqual(post.call_count, 1)

    @patch.object(AskTheBookService, "upload_document", return_value=DOCUMENT)
    @patch.object(AskTheBookService, "ask", return_value=ANSWER)
    def test_attach_ask_sources_history_and_return_to_normal(self, ask, upload):
        view = ChatView()
        provider = Mock()
        provider.send_message.return_value = "Normal answer"
        settings = ChatbotSettings(askthebook_enabled=True, model="normal-model", askthebook_model="pdf-model")
        session = ChatSession(chat_type="pdf")
        controller = ChatController(view, session, settings, provider)
        self.assertTrue(view.attach_pdf_btn.isEnabled())
        controller.attach_pdf("example.pdf")
        self.assertFalse(view.attach_pdf_btn.isEnabled())
        self.wait_request(controller)
        self.assertEqual(view.selected_document(), DOCUMENT)
        controller.ask("What is on page three?")
        self.wait_request(controller)
        ask.assert_called_once_with(document_id="doc-1", question="What is on page three?", model="pdf-model")
        provider.send_message.assert_not_called()
        self.assertEqual(session.to_payload(), [])
        self.assertEqual(session.messages[-1].sources, ANSWER["sources"])
        restored = ChatHistoryItem.from_dict(ChatHistoryItem(session=session).to_dict())
        self.assertEqual(restored.session.messages, session.messages)
        self.assertEqual(restored.session.chat_type, "pdf")
        self.assertEqual(restored.session.document, DOCUMENT)
        view.render_session(restored.session)
        source_buttons = [button for button in view.findChildren(QPushButton) if button.text() == "Sources (1)"]
        self.assertTrue(source_buttons)
        source_buttons[-1].click()
        self.assertTrue(any("Physical PDF page: 3" in box.toPlainText() for box in view.findChildren(QPlainTextEdit)))
        view.document_input.setCurrentIndex(0)
        controller.ask("No document selected")
        provider.send_message.assert_not_called()
        self.assertFalse(controller.busy)
        controller.set_session(ChatSession())
        self.assertTrue(view.document_controls.isHidden())
        controller.ask("Normal question")
        self.wait_request(controller)
        self.assertEqual(provider.send_message.call_args.kwargs["messages"], [{"role": "user", "content": "Normal question"}])
        controller.ask("Follow-up")
        self.wait_request(controller)
        self.assertEqual(len(provider.send_message.call_args.kwargs["messages"]), 3)
        controller.set_session(restored.session)
        self.assertEqual(view.selected_document(), DOCUMENT)
        view.close()

    @patch.object(AskTheBookService, "list_documents", side_effect=RuntimeError("Service busy (HTTP 409)"))
    def test_failure_restores_controls_and_normal_chat(self, listing):
        view = ChatView()
        provider = Mock()
        provider.send_message.return_value = "OK"
        controller = ChatController(view, ChatSession(chat_type="pdf"), ChatbotSettings(askthebook_enabled=True, model="m"), provider)
        controller.refresh_documents()
        self.wait_request(controller)
        self.assertTrue(view.question_input.isEnabled())
        self.assertTrue(view.attach_pdf_btn.isEnabled())
        listing.assert_called_once()
        controller.set_session(ChatSession())
        controller.ask("Normal question")
        self.wait_request(controller)
        provider.send_message.assert_called_once()
        view.close()

    def test_creation_buttons_choose_and_preserve_type(self):
        from promptlet_client.controller.chat_history_controller import ChatHistoryController
        from promptlet_client.view.chat_history_view import ChatHistoryView
        view = ChatHistoryView()
        repository = Mock()
        repository.load.return_value = [ChatHistoryItem()]
        controller = ChatHistoryController(view, repository)
        view.new_pdf_chat_btn.click()
        pdf_id = controller.active_chat_id
        self.assertEqual(controller.active_chat.session.chat_type, "pdf")
        self.assertIn("[PDF]", view.chat_list.item(0).text())
        view.new_chat_btn.click()
        self.assertEqual(controller.active_chat.session.chat_type, "normal")
        controller.select_chat(pdf_id)
        self.assertEqual(controller.active_chat.session.chat_type, "pdf")
        view.close()


if __name__ == "__main__":
    unittest.main()
