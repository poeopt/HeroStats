from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from src.consts.i18n import t
from src.engine import Engine

_RC = {
    "Satanic": "#CA1717", "Angelic": "#F6F794", "Unholy": "#c8c050",
    "Heroic": "#00FFAE",  "Mythic":  "#C050FF", "Rare":   "#5090C0",
    "Superior": "#50A050","Common":  "#5a4a30",
}
_WIN = """
QWidget { background:#181212; }
QScrollArea { border:none; }
"""
_HDR_BTN = ("QPushButton{background:#0f0808;border:1px solid #2a1010;"
            "color:#5a3020;font-size:9px;padding:1px 6px;border-radius:2px;}"
            "QPushButton:hover{color:#C3AF75;border-color:#C3AF75;}")


class _Row(QWidget):
    def __init__(self, entry, idx: int):
        QWidget.__init__(self)
        self.setFixedHeight(20)
        self.setStyleSheet(
            "QWidget{background:#0f0808;border-bottom:1px solid #150d0d;}"
            "QWidget:hover{background:#140a0a;}")
        lo = QHBoxLayout(self)
        lo.setContentsMargins(6, 0, 6, 0)
        lo.setSpacing(5)
        c = _RC.get(entry.rarity, "#6a5030")

        def lbl(txt, w, cl=c):
            l = QLabel(txt)
            l.setStyleSheet(
                f"color:{cl};font-size:10px;font-family:'CookieRun Bold';"
                "background:transparent;border:none;")
            l.setFixedWidth(w)
            return l

        lo.addWidget(lbl(f"#{idx+1}", 22, "#2a1a10"))
        lo.addWidget(lbl(entry.time,   54, "#3a2010"))
        lo.addWidget(lbl(entry.rarity, 68, c))
        lo.addWidget(lbl(f"T{entry.tier}", 24, "#7a6030"))
        lo.addWidget(lbl(f"Q{entry.quality}", 24, "#7a6030"))
        socks = f"{entry.sockets}s" if entry.sockets > 0 else ""
        lo.addWidget(lbl(socks, 22, "#5a4020"))
        mf = "✦" if entry.mf_drop else ""
        lo.addWidget(lbl(mf, 14, "#4040A0"))
        lo.addStretch()


class DropLogWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self, None,
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint)
        self.setObjectName("DropLogWindow")
        self.setStyleSheet(_WIN)
        self.setFixedWidth(300)

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        # Custom title bar (no white OS bar)
        hdr = QWidget()
        hdr.setFixedHeight(24)
        hdr.setStyleSheet("background:#0a0606;border-bottom:1px solid #180e0e;")
        hdr_lo = QHBoxLayout(hdr)
        hdr_lo.setContentsMargins(8, 0, 6, 0)
        hdr_lo.setSpacing(4)
        title = QLabel(t("win_drops").upper())
        title.setStyleSheet("color:#5a3020;font-size:9px;letter-spacing:1px;"
                            "font-family:'CookieRun Bold';background:transparent;border:none;")
        self._cnt = QLabel("0")
        self._cnt.setStyleSheet("color:#3a1a10;font-size:9px;font-family:'CookieRun Bold';"
                                "background:transparent;border:none;")
        clr_btn = QPushButton(t("clear"))
        clr_btn.setFixedSize(48, 16)
        clr_btn.setStyleSheet(_HDR_BTN)
        clr_btn.clicked.connect(self._clear)
        hdr_lo.addWidget(title)
        hdr_lo.addStretch()
        hdr_lo.addWidget(self._cnt)
        hdr_lo.addWidget(clr_btn)
        lo.addWidget(hdr)

        # Drag support for frameless window
        self._drag_pos = None
        hdr.mousePressEvent   = self._hdr_press
        hdr.mouseMoveEvent    = self._hdr_move
        hdr.mouseReleaseEvent = self._hdr_release

        # Scroll
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._content = QWidget()
        self._content.setStyleSheet("background:#181212;")
        self._clo = QVBoxLayout(self._content)
        self._clo.setContentsMargins(0, 0, 0, 0)
        self._clo.setSpacing(0)
        self._clo.addStretch()
        self._scroll.setWidget(self._content)
        lo.addWidget(self._scroll)

        # Stats bar
        self._stats = QLabel("")
        self._stats.setStyleSheet(
            "background:#0a0606;color:#4a2a10;font-size:9px;padding:2px 8px;"
            "border-top:1px solid #150a0a;font-family:'CookieRun Bold';")
        lo.addWidget(self._stats)

        self._last_count = -1
        QTimer(self, timeout=self._refresh, interval=300).start()

    def _hdr_press(self, e):
        from PySide6.QtCore import Qt as Q
        if e.button() == Q.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def _hdr_move(self, e):
        from PySide6.QtCore import Qt as Q
        if self._drag_pos and e.buttons() & Q.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
    def _hdr_release(self, e):
        self._drag_pos = None

    def _clear(self):
        Engine.game_stats.drop_log.reset()
        self._last_count = -1

    def _refresh(self):
        entries = Engine.game_stats.drop_log.entries
        if len(entries) == self._last_count:
            return
        self._last_count = len(entries)
        self._cnt.setText(str(len(entries)))

        while self._clo.count():
            item = self._clo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not entries:
            ph = QLabel(f"  {t('no_drops')}")
            ph.setStyleSheet("color:#2a1a10;padding:10px;font-size:11px;"
                             "font-family:'CookieRun Bold';background:transparent;border:none;")
            self._clo.addWidget(ph)
            self._stats.setText("")
        else:
            for i, e in enumerate(entries):
                self._clo.addWidget(_Row(e, i))
            sat = sum(1 for e in entries if e.rarity == "Satanic")
            ang = sum(1 for e in entries if e.rarity in ("Angelic","Unholy"))
            her = sum(1 for e in entries if e.rarity == "Heroic")
            mf  = sum(1 for e in entries if e.mf_drop)
            self._stats.setText(
                f"Всего:{len(entries)}  Сат:{sat}  Анг:{ang}  Гер:{her}  MF:{mf}")
        self._clo.addStretch()
        target_h = min(max(len(entries) * 20 + 70, 100), 400)
        self.setFixedHeight(target_h)

    def retranslate(self):
        pass
