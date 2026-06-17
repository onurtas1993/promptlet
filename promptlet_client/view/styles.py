APP_STYLESHEET = """
    QWidget {
        background-color: #181818;
        color: white;
        font-family: Consolas, monospace;
        font-size: 18px;
    }

    QLabel {
        color: #ff9f1c;
        font-weight: bold;
        font-size: 18px;
    }

    QLineEdit {
        background-color: #262626;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px;
        font-size: 18px;
    }

    QTextEdit {
        background-color: #181818;
        color: white;
        border: none;
        font-size: 18px;
    }

    QPushButton {
        border: none;
        background: transparent;
        font-size: 22px;
    }
"""

TITLE_STYLESHEET = """
    color:#dddddd;
    font-size:40px;
    font-weight:normal;
"""

SETTINGS_BUTTON_STYLESHEET = "color:#ff9f1c;"
SAVE_BUTTON_STYLESHEET = "color:#2eff9b;"
CANCEL_BUTTON_STYLESHEET = "color:#aaaaaa;"
RESET_BUTTON_STYLESHEET = "color:#ff4fc3;"

HISTORY_STYLESHEET = """
    QWidget {
        background-color: #111111;
        color: white;
        font-family: Consolas, monospace;
        font-size: 16px;
    }

    QLabel {
        color: #ff9f1c;
        font-weight: bold;
        font-size: 22px;
    }

    QListWidget {
        background-color: #181818;
        color: white;
        border: none;
        padding: 4px;
    }

    QListWidget::item {
        padding: 10px;
        border-radius: 4px;
    }

    QListWidget::item:selected {
        background-color: #2a2a2a;
    }
"""

NEW_CHAT_BUTTON_STYLESHEET = "color:#2eff9b; text-align:left; padding:8px;"
DELETE_BUTTON_STYLESHEET = "color:#ff5555; text-align:left; padding:8px;"
