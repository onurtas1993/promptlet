from PySide6.QtCore import Signal
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

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.resize(600, 400)
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

    def set_settings(self, settings: ChatbotSettings) -> None:
        provider_index = self.provider_input.findText(settings.provider)
        if provider_index >= 0:
            self.provider_input.setCurrentIndex(provider_index)

        self.attr_input.setText(settings.attributes)
        self.key_input.setText(settings.api_key)
        self.base_url_input.setText(settings.base_url)
        self.model_input.setText(settings.model)
        self.max_tokens_spin.setValue(settings.max_tokens)

    def current_settings(self) -> ChatbotSettings:
        return ChatbotSettings(
            provider=self.provider_input.currentText(),
            attributes=self.attr_input.text(),
            api_key=self.key_input.text(),
            base_url=self.base_url_input.text(),
            model=self.model_input.text(),
            max_tokens=self.max_tokens_spin.value(),
        )

    def _emit_settings_saved(self) -> None:
        self.settings_saved.emit(self.current_settings())
        self.close()
