from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog

from promptlet_client.model.chatbot_settings import ChatbotSettings
from promptlet_client.view.ui_loader import load_ui
from promptlet_client.view.styles import (
    APP_STYLESHEET,
    CANCEL_BUTTON_STYLESHEET,
    SAVE_BUTTON_STYLESHEET,
)


class SettingsView(QDialog):
    settings_saved = Signal(ChatbotSettings)
    documents_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 760)
        self._documents_busy = False
        self.setStyleSheet(APP_STYLESHEET)

        self._load_ui()
        self._apply_styles()
        self._connect_signals()

    def _load_ui(self) -> None:
        load_ui(self, "settings_view.ui")

    def _apply_styles(self) -> None:
        self.save_btn.setStyleSheet(SAVE_BUTTON_STYLESHEET)
        self.cancel_btn.setStyleSheet(CANCEL_BUTTON_STYLESHEET)

    def _connect_signals(self) -> None:
        self.save_btn.clicked.connect(self._emit_settings_saved)
        self.cancel_btn.clicked.connect(self.close)
        self.lm_studio_btn.clicked.connect(self._use_lm_studio)
        self.askthebook_enabled_input.toggled.connect(self._update_integration_controls)
        self.askthebook_url_input.textChanged.connect(self.documents_output.clear)
        self.refresh_documents_btn.clicked.connect(
            lambda: self.documents_requested.emit(self.askthebook_url_input.text())
        )

    def _use_lm_studio(self) -> None:
        defaults = ChatbotSettings()
        self.provider_input.setCurrentText(defaults.provider)
        self.base_url_input.setText(defaults.base_url)
        self.key_input.clear()
        self.model_input.clear()
        self.model_input.setFocus()

    def _update_integration_controls(self) -> None:
        enabled = self.askthebook_enabled_input.isChecked()
        self.askthebook_url_input.setEnabled(enabled and not self._documents_busy)
        self.askthebook_model_input.setEnabled(enabled)
        self.refresh_documents_btn.setEnabled(enabled and not self._documents_busy)
        self.askthebook_enabled_input.setEnabled(not self._documents_busy)
        if not enabled:
            self.documents_output.clear()

    def set_documents_busy(self, busy: bool) -> None:
        self._documents_busy = busy
        self._update_integration_controls()
        if busy:
            self.documents_output.setPlainText("Loading prepared documents...")

    @Slot(object)
    def show_documents(self, documents: list[dict]) -> None:
        lines = []
        for document in documents:
            pages = f"{document['pages']} pages, " if "pages" in document else ""
            lines.append(
                f"{document['name']} — {pages}{document.get('chunks', '?')} chunks\n"
                f"ID: {document['document_id']}"
            )
        self.documents_output.setPlainText("\n\n".join(lines) or "No prepared documents.")

    def set_settings(self, settings: ChatbotSettings) -> None:
        provider_index = self.provider_input.findText(settings.provider)
        if provider_index >= 0:
            self.provider_input.setCurrentIndex(provider_index)

        self.attr_input.setText(settings.attributes)
        self.key_input.setText(settings.api_key)
        self.base_url_input.setText(settings.base_url)
        self.model_input.setText(settings.model)
        self.max_tokens_spin.setValue(settings.max_tokens)
        self.askthebook_enabled_input.setChecked(settings.askthebook_enabled)
        self.askthebook_url_input.setText(settings.askthebook_url)
        self.askthebook_model_input.setText(settings.askthebook_model)
        self._update_integration_controls()

    def current_settings(self) -> ChatbotSettings:
        return ChatbotSettings(
            provider=self.provider_input.currentText(),
            attributes=self.attr_input.text(),
            api_key=self.key_input.text(),
            base_url=self.base_url_input.text(),
            model=self.model_input.text(),
            max_tokens=self.max_tokens_spin.value(),
            askthebook_enabled=self.askthebook_enabled_input.isChecked(),
            askthebook_url=self.askthebook_url_input.text().strip(),
            askthebook_model=self.askthebook_model_input.text().strip(),
        )

    def _emit_settings_saved(self) -> None:
        self.settings_saved.emit(self.current_settings())
        self.close()
