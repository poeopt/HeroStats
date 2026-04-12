style = """
QWidget {
    font-family: "CookieRun Bold";
    font-size: 13px;
    color: #C3AF75;
    background: transparent;
}
QWidget#MainWidget  { background: #181212; }
QWidget#InnerWidget { background: #181212; }

QFrame#GroupBox, QFrame#GroupBoxXL {
    background: #0f0e0d;
    border: 1px solid #2a1414;
    border-top: 1px solid #181212;
    border-bottom: 2px solid #3a1a1a;
}
QScrollBar:vertical {
    background: #0a0808; width: 5px; margin: 0;
}
QScrollBar::handle:vertical {
    background: #3a1414; border-radius: 2px; min-height: 16px;
}
QScrollBar::handle:vertical:hover { background: #5a2020; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 5px; background: #0a0808; }
QScrollBar::handle:horizontal { background: #3a1414; border-radius: 2px; }
QLabel#MailActive   { color: #F6C94E; font-size: 12px; }
QLabel#MailInactive { color: #2a1a10; font-size: 10px; }
QToolTip {
    background: #0f0808; color: #C3AF75;
    border: 1px solid #3a1414; padding: 4px 7px;
    font-size: 11px; border-radius: 2px;
}
QPushButton#ResetButton {
    background: #150a0a; border: 1px solid #3a1414;
    border-bottom: 2px solid #5a1a1a; border-radius: 2px;
    color: #C3AF75; font-size: 11px; padding: 1px 8px;
}
QPushButton#ResetButton:hover  { background: #200d0d; border-color: #8a2020; }
QPushButton#ResetButton:pressed { border-bottom-width: 1px; }
QPushButton#CopyButton {
    background: #150a0a; border: 1px solid #2a1212;
    border-radius: 2px; color: #6a5030; font-size: 11px; padding: 1px 5px;
}
QPushButton#CopyButton:hover { color: #C3AF75; border-color: #C3AF75; }
QLineEdit {
    background: #0a0808; border: 1px solid #2a1414;
    color: #9a8060; font-size: 10px;
    padding: 1px 4px; border-radius: 2px;
    selection-background-color: #3a1414;
}
QLineEdit:focus  { border-color: #5a2020; color: #C3AF75; }
"""
