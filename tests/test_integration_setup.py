import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from PySide6.QtWidgets import QApplication

from promptlet_client.controller.settings_controller import SettingsController
from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.provider.openai_provider import OpenAIProvider
from promptlet_client.repository.settings_repository import SettingsRepository
from promptlet_client.service.askthebook_service import AskTheBookService
from promptlet_client.view.settings_view import SettingsView


class IntegrationSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_settings_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = SettingsRepository()
            repository.APP_DIR = Path(directory)
            repository.SETTINGS_FILE = Path(directory) / "settings.json"
            settings = ChatbotSettings(askthebook_url="http://localhost:9000", askthebook_model="my-model")
            repository.save(settings)
            self.assertEqual(repository.load(), settings)

    @patch("promptlet_client.provider.openai_provider.requests.post")
    def test_local_chat_omits_empty_authentication(self, post):
        post.return_value.json.return_value = {"choices": [{"message": {"content": "answer"}}]}
        settings = ChatbotSettings(model="chosen-model")
        self.assertEqual(OpenAIProvider().send_message(settings, "system", []), "answer")
        self.assertEqual(post.call_args.args[0], "http://127.0.0.1:1234/v1/chat/completions")
        self.assertNotIn("authorization", post.call_args.kwargs["headers"])
        self.assertEqual(post.call_args.kwargs["json"]["model"], "chosen-model")
        settings.api_key = "token"
        OpenAIProvider().send_message(settings, "system", [])
        self.assertEqual(post.call_args.kwargs["headers"]["authorization"], "Bearer token")

    @patch("promptlet_client.service.askthebook_service.requests.get")
    def test_documents_missing_pages_and_empty_list(self, get):
        get.return_value.ok = True
        documents = [{"document_id": "existing", "name": "book.pdf", "chunks": 2}]
        get.return_value.json.return_value = {"documents": documents}
        service = AskTheBookService("http://localhost:9000/")
        self.assertEqual(service.list_documents(), documents)
        get.assert_called_once_with("http://localhost:9000/documents", timeout=(5, 30))
        get.return_value.json.return_value = {"documents": []}
        self.assertEqual(service.list_documents(), [])

    @patch("promptlet_client.service.askthebook_service.requests.get")
    def test_service_errors(self, get):
        service = AskTheBookService("http://localhost:8000")
        for status, detail, expected in [(409, "processing", "busy"), (422, [{"msg": "bad input"}], "bad input"), (503, "dependency missing", "dependency missing")]:
            with self.subTest(status=status):
                get.return_value.ok = False
                get.return_value.status_code = status
                get.return_value.json.return_value = {"detail": detail}
                with self.assertRaisesRegex(RuntimeError, expected):
                    service.list_documents()
        get.reset_mock()
        get.side_effect = requests.Timeout()
        with self.assertRaisesRegex(RuntimeError, "timed out"):
            service.list_documents()
        self.assertEqual(get.call_count, 1)
        get.side_effect = requests.ConnectionError()
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            service.list_documents()

    @patch("promptlet_client.service.askthebook_service.requests.get")
    def test_malformed_list(self, get):
        get.return_value.ok = True
        get.return_value.json.return_value = {"documents": [{}]}
        with self.assertRaisesRegex(RuntimeError, "invalid document list"):
            AskTheBookService("http://localhost:8000").list_documents()

    @patch("promptlet_client.service.askthebook_service.requests.get")
    def test_settings_ui_background_listing_and_cleanup(self, get):
        get.return_value.ok = True
        get.return_value.json.return_value = {"documents": [{"document_id": "existing", "name": "book.pdf", "chunks": 2}]}
        view = SettingsView()
        repository = Mock()
        repository.load.return_value = ChatbotSettings()
        controller = SettingsController(view, repository)
        self.assertEqual(view.askthebook_group.title(), "AskTheBook Integration")
        view.refresh_documents_btn.click()
        self.assertTrue(controller.busy)
        deadline = time.monotonic() + 3
        while controller.busy and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.005)
        self.assertFalse(controller.busy)
        self.assertIn("book.pdf", view.documents_output.toPlainText())
        self.assertTrue(view.refresh_documents_btn.isEnabled())
        self.assertEqual(view.base_url_input.placeholderText(), "http://127.0.0.1:1234")
        self.assertEqual(view.key_input.placeholderText(), "Optional for local LLM")
        view.close()


if __name__ == "__main__":
    unittest.main()
