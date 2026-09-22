from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QPlainTextEdit, QWidget
from markdown import markdown


class MessageWidget(QWidget):
    def __init__(
        self,
        speaker: str,
        text: str,
        color: str,
        is_user: bool = False,
        metadata=None,
    ) -> None:
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)

        label = QLabel()
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        text = markdown(text, extensions=["fenced_code", "tables"])

        label.setText(
            f"""
            <span style="color:white; font-weight:bold;">
                {speaker}:
            </span>
            <div style="color:{color};">
                {text}
            </div>
            """
        )

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(label)
        if metadata is not None and metadata.document:
            attribution = QLabel(f"Document: {metadata.document['name']}")
            attribution.setTextFormat(Qt.PlainText)
            content_layout.addWidget(attribution)
            for warning in metadata.warnings:
                warning_label = QLabel(f"Warning: {warning}")
                warning_label.setTextFormat(Qt.PlainText)
                warning_label.setWordWrap(True)
                content_layout.addWidget(warning_label)
            if metadata.sources:
                toggle = QPushButton(f"Sources ({len(metadata.sources)})")
                toggle.setCheckable(True)
                details = QPlainTextEdit()
                details.setReadOnly(True)
                details.setMinimumHeight(180)
                # Keep every backend field inspectable without guessing its source schema.
                details.setPlainText("\n\n".join(
                    "\n".join(f"{'Physical PDF page' if key == 'page' else key}: {value}" for key, value in source.items())
                    for source in metadata.sources
                ))
                details.hide()
                toggle.toggled.connect(details.setVisible)
                content_layout.addWidget(toggle)
                content_layout.addWidget(details)

        if is_user:
            layout.addStretch()
            layout.addWidget(content)
        else:
            layout.addWidget(content)
            layout.addStretch()
