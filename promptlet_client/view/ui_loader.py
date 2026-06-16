from pathlib import Path

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QLayout, QVBoxLayout, QWidget


def load_ui(owner: QWidget, ui_name: str | None = None) -> QWidget:
    """Load a .ui file next to the calling view and expose named widgets on owner.

    This keeps view classes close to the PyQt style:
        load_ui(self)
    """
    caller_file = Path(owner.__class__.__module__.replace(".", "/"))
    ui_path = Path(__file__).with_name(ui_name or f"{caller_file.name}.ui")

    ui_file = QFile(str(ui_path))
    if not ui_file.open(QFile.ReadOnly):
        raise RuntimeError(f"Unable to open UI file: {ui_path}")

    try:
        form = QUiLoader().load(ui_file, owner)
    finally:
        ui_file.close()

    if form is None:
        raise RuntimeError(f"Unable to load UI file: {ui_path}")

    layout = QVBoxLayout(owner)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(form)

    for child in form.findChildren(QWidget) + form.findChildren(QLayout):
        name = child.objectName()
        if name:
            setattr(owner, name, child)

    return form
