import sys
from pathlib import Path
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


def resource_path(path: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / path
    return Path(__file__).parent.parent / path
