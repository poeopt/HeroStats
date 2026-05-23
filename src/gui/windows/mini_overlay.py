"""
Mini Overlay — компактное окно поверх игры.
Хоткей Ctrl+M — переключение. Двойной клик — развернуть главное окно.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QFont, QPainter, QColor, QPainterPath, QLinearGradient


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


class MiniOverlay(QWidget):
    def __init__(self, on_expand=None):
        QWidget.__init__(self, None,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool)
        self.setObjectName("MiniOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._on_expand = on_expand
        self._drag: QPoint | None = None
        self._hotkey = "Ctrl+M"

        self.setFixedSize(190, 100)

        lo = QVBoxLayout(self)
        lo.setContentsMargins(10, 7, 10, 7)
        lo.setSpacing(4)

        # Header: dot + title + hint
        top = QHBoxLayout(); top.setSpacing(5)
        self._dot = QLabel("●")
        self._dot.setFixedWidth(10)
        self._dot.setStyleSheet("color:#CA1717; font-size:8px;")
        title = QLabel("HERO SIEGE STATS")
        title.setStyleSheet(
            "color:rgba(200,160,100,120); font-size:8px;"
            "letter-spacing:2px; font-family:'CookieRun Bold';")
        hint = QLabel("×2 ↑")
        hint.setStyleSheet("color:rgba(100,60,30,150); font-size:8px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignRight)
        top.addWidget(self._dot)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(hint)
        lo.addLayout(top)

        # Stats rows
        def make_row(icon, icon_color, val_color):
            r = QHBoxLayout(); r.setSpacing(6)
            ic = QLabel(icon)
            ic.setFixedWidth(18)
            ic.setStyleSheet(f"color:{icon_color}; font-size:11px; font-family:'CookieRun Bold';")
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v = QLabel("—")
            v.setStyleSheet(
                f"color:{val_color}; font-size:14px; font-family:'CookieRun Bold';"
                "font-weight:bold;")
            u = QLabel("")
            u.setFixedWidth(24)
            u.setStyleSheet("color:rgba(120,80,30,180); font-size:9px; font-family:'CookieRun Bold';")
            r.addWidget(ic); r.addWidget(v); r.addWidget(u); r.addStretch()
            return r, v, u

        r1, self._gold_val, self._gold_unit = make_row("G", "#C8A850", "#E0C870")
        r2, self._xp_val,   self._xp_unit   = make_row("X", "#9060E0", "#B090FF")
        r3, self._drop_val, self._drop_unit  = make_row("D", "#CA1717", "#FF5050")

        lo.addLayout(r1)
        lo.addLayout(r2)
        lo.addLayout(r3)

        # Dot blink timer
        self._blink = True
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink_dot)
        self._blink_timer.start(1200)

        QTimer(self, timeout=self._refresh, interval=1000).start()

    def paintEvent(self, e):
        """Рисуем закруглённый полупрозрачный фон вручную."""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)

        # Градиент фон
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor(18, 8, 8, 220))
        grad.setColorAt(1.0, QColor(10, 5, 5, 200))
        p.fillPath(path, grad)

        # Рамка
        p.setPen(QColor(100, 20, 20, 160))
        p.drawPath(path)

        # Акцентная линия сверху
        from PySide6.QtGui import QPen
        pen = QPen(QColor(180, 30, 30, 120))
        pen.setWidth(2)
        p.setPen(pen)
        p.drawLine(10, 1, self.width() - 10, 1)

    def _blink_dot(self):
        self._blink = not self._blink
        color = "#CA1717" if self._blink else "#400808"
        self._dot.setStyleSheet(f"color:{color}; font-size:8px;")

    def _refresh(self):
        try:
            from src.engine import Engine
            stats = Engine.get_stats()
            g = stats.gold
            x = stats.xp
            items = stats.added_items.added_items

            self._gold_val.setText(_fmt(g.gold_per_hour))
            self._gold_unit.setText("/ч")

            self._xp_val.setText(_fmt(x.xp_per_hour))
            self._xp_unit.setText("/ч")

            sat = items.get("Satanic", {}).get("total", 0)
            ang = (items.get("Angelic", {}).get("total", 0)
                   + items.get("Unholy", {}).get("total", 0))
            her = items.get("Heroic", {}).get("total", 0)
            self._drop_val.setText(f"S:{sat} A:{ang}")
            self._drop_unit.setText(f"H:{her}")
        except Exception:
            pass

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = None

    def mouseDoubleClickEvent(self, e):
        if self._on_expand:
            self._on_expand()

    def retranslate(self): pass
