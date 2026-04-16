from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QPoint
from src.consts.i18n import t
from src.engine import Engine

_RC = {
    "Satanic": "#CA1717", "Angelic": "#F6F794", "Unholy": "#c8c050",
    "Heroic":  "#00FFAE", "Mythic":  "#C050FF", "Rare":   "#5090C0",
    "Superior":"#50A050", "Common":  "#5a4a30",
}


class _Row(QWidget):
    def __init__(self, entry, idx: int):
        QWidget.__init__(self)
        self.setObjectName("DropRow")
        self.setFixedHeight(20)
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
        self.setFixedWidth(300)
        self._drag: QPoint | None = None

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        # Titlebar
        hdr = QWidget()
        hdr.setObjectName("WinHeader")
        hdr.setFixedHeight(24)
        hdr_lo = QHBoxLayout(hdr)
        hdr_lo.setContentsMargins(8, 0, 6, 0)
        hdr_lo.setSpacing(4)

        title = QLabel("DROP LOG")
        title.setObjectName("WinTitle")

        self._cnt = QLabel("0")
        self._cnt.setObjectName("BDesc")

        clr_btn = QPushButton(t("clear"))
        clr_btn.setObjectName("SettingsBtn")
        clr_btn.setFixedSize(48, 16)
        clr_btn.clicked.connect(self._clear)

        hdr_lo.addWidget(title)
        hdr_lo.addStretch()
        hdr_lo.addWidget(self._cnt)
        hdr_lo.addWidget(clr_btn)
        lo.addWidget(hdr)

        # Drag
        hdr.mousePressEvent   = self._hp
        hdr.mouseMoveEvent    = self._hm
        hdr.mouseReleaseEvent = self._hr

        # Scroll
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)

        self._content = QWidget()
        self._content.setObjectName("DropLogWindow")
        self._clo = QVBoxLayout(self._content)
        self._clo.setContentsMargins(0, 0, 0, 0)
        self._clo.setSpacing(0)
        self._clo.addStretch()
        self._scroll.setWidget(self._content)
        lo.addWidget(self._scroll)

        # Stats bar
        self._stats = QLabel("")
        self._stats.setObjectName("BDesc")
        self._stats.setStyleSheet("padding:2px 8px; border-top:1px solid #150a0a;")
        lo.addWidget(self._stats)

        self._last_count = -1
        QTimer(self, timeout=self._refresh, interval=300).start()

    def _hp(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _hm(self, e):
        if self._drag and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def _hr(self, e):
        self._drag = None

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
            ph.setObjectName("BDesc")
            ph.setStyleSheet("padding:10px;")
            self._clo.addWidget(ph)
            self._stats.setText("")
        else:
            for i, e in enumerate(entries):
                self._clo.addWidget(_Row(e, i))
            sat = sum(1 for e in entries if e.rarity == "Satanic")
            ang = sum(1 for e in entries if e.rarity in ("Angelic", "Unholy"))
            her = sum(1 for e in entries if e.rarity == "Heroic")
            mf  = sum(1 for e in entries if e.mf_drop)
            self._stats.setText(
                f"Всего:{len(entries)}  Сат:{sat}  Анг:{ang}  Гер:{her}  MF:{mf}")
        self._clo.addStretch()
        self.setFixedHeight(min(max(len(entries) * 20 + 70, 100), 400))

    def retranslate(self): pass
