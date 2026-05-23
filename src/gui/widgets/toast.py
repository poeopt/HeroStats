from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QApplication
from PySide6.QtCore import Qt, QTimer

_STYLES = {
    "Satanic": ("#2a0505", "#CA1717", "#ff4040"),
    "Angelic":  ("#202000", "#F6F794", "#ffff50"),
    "Unholy":   ("#202000", "#F6F794", "#ffff50"),
    "Heroic":   ("#052015", "#00FFAE", "#00ffaa"),
    "Mail":     ("#102010", "#F6C94E", "#f6c94e"),
}
_DEF = ("#181212", "#C3AF75", "#C3AF75")
_ICONS = {"Satanic": "💀", "Angelic": "👼", "Unholy": "👼",
          "Heroic": "⚔️",   "Mail":    "✉️"}


class ToastWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.BypassWindowManagerHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)

        lo = QHBoxLayout(self)
        lo.setContentsMargins(12, 7, 12, 7)
        lo.setSpacing(7)

        from PySide6.QtGui import QFont
        self._icon = QLabel()
        self._icon.setFont(QFont("Segoe UI Emoji", 16))
        self._text = QLabel()
        self._text.setFont(QFont("CookieRun Bold", 12))
        lo.addWidget(self._icon)
        lo.addWidget(self._text)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self.hide()

    def show_drop(self, rarity: str, text: str):
        bg, fg, border = _STYLES.get(rarity, _DEF)
        icon = _ICONS.get(rarity, "📦")
        self._icon.setText(icon)
        self._icon.setStyleSheet(f"color:{fg};")
        self._text.setText(text)
        self._text.setStyleSheet(f"color:{fg};")
        self.setStyleSheet(
            f"QWidget{{background:{bg}; border:2px solid {border}; border-radius:5px;}}")
        self.adjustSize()
        scr = QApplication.primaryScreen().geometry()
        self.move(scr.right() - self.width() - 16, scr.top() + 55)
        self.show(); self.raise_()
        self._timer.start(3500)
