from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QWidget


class MessageWidget(QWidget):
    def __init__(
        self,
        speaker: str,
        text: str,
        color: str,
        is_user: bool = False,
    ) -> None:
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)

        label = QLabel()
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        text = text.replace("\n", "<br>")

        label.setText(
            f"""
            <span style="color:white; font-weight:bold;">
                {speaker}:
            </span>
            <span style="color:{color};">
                {text}
            </span>
            """
        )

        if is_user:
            layout.addStretch()
            layout.addWidget(label)
        else:
            layout.addWidget(label)
            layout.addStretch()