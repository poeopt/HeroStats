from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QPoint
from src.engine import Engine

_ACT_COLORS = [
    "#CA1717","#C07030","#90A030","#30A060",
    "#3080C0","#9030C0","#C03080","#707070",
]


class ChaosWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self, None,
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint)
        self.setObjectName("ChaosWindow")
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
        title = QLabel("🗼  БАШНЯ ХАОСА · ВОРМХОЛ")
        title.setObjectName("WinTitle")
        hdr_lo.addWidget(title)
        lo.addWidget(hdr)

        hdr.mousePressEvent   = self._hp
        hdr.mouseMoveEvent    = self._hm
        hdr.mouseReleaseEvent = self._hr

        # Body
        body = QWidget()
        body.setObjectName("ChaosWindow")
        body_lo = QVBoxLayout(body)
        body_lo.setContentsMargins(10, 8, 10, 10)
        body_lo.setSpacing(4)
        lo.addWidget(body)

        def sec(txt):
            l = QLabel(txt)
            l.setObjectName("WinTitle")
            l.setStyleSheet("margin-top:4px;margin-bottom:2px;letter-spacing:1px;")
            return l

        def row_pair(label_txt):
            r = QHBoxLayout(); r.setSpacing(6)
            lbl = QLabel(label_txt)
            lbl.setObjectName("BDesc")
            lbl.setFixedWidth(110)
            val = QLabel("0")
            val.setObjectName("CharName")
            r.addWidget(lbl); r.addWidget(val); r.addStretch()
            return r, val

        body_lo.addWidget(sec("CHAOS TOWER"))
        r1, self._ct_total   = row_pair("Total cleared:")
        r2, self._ct_session = row_pair("This session:")
        r3, self._ct_bosses  = row_pair("Boss kills:")
        body_lo.addLayout(r1)
        body_lo.addLayout(r2)
        body_lo.addLayout(r3)

        body_lo.addSpacing(6)
        body_lo.addWidget(sec("WORMHOLE LEVELS"))

        self._wh_bars: list[QProgressBar] = []
        self._wh_vals: list[QLabel] = []

        grid = QHBoxLayout(); grid.setSpacing(10)
        col1 = QVBoxLayout(); col1.setSpacing(3)
        col2 = QVBoxLayout(); col2.setSpacing(3)

        for i in range(8):
            c = _ACT_COLORS[i]
            row_lo = QHBoxLayout(); row_lo.setSpacing(4)
            a_lbl = QLabel(f"A{i+1}")
            a_lbl.setFixedWidth(18)
            a_lbl.setStyleSheet(
                f"color:{c};font-size:9px;font-family:'CookieRun Bold';"
                "background:transparent;border:none;")
            bar = QProgressBar()
            bar.setRange(0, 10); bar.setValue(0)
            bar.setTextVisible(False); bar.setFixedHeight(6)
            bar.setStyleSheet(
                f"QProgressBar{{background:transparent;border:none;border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{c};border-radius:2px;}}")
            v_lbl = QLabel("0")
            v_lbl.setFixedWidth(18)
            v_lbl.setStyleSheet(
                f"color:{c};font-size:9px;font-family:'CookieRun Bold';"
                "background:transparent;border:none;")
            row_lo.addWidget(a_lbl); row_lo.addWidget(bar, 1); row_lo.addWidget(v_lbl)
            self._wh_bars.append(bar)
            self._wh_vals.append(v_lbl)
            (col1 if i < 4 else col2).addLayout(row_lo)

        grid.addLayout(col1, 1); grid.addLayout(col2, 1)
        body_lo.addLayout(grid)

        self._best = QLabel("Best: 0  ·  Total: 0")
        self._best.setObjectName("BDesc")
        self._best.setStyleSheet("margin-top:4px;")
        body_lo.addWidget(self._best)

        QTimer(self, timeout=self._refresh, interval=1000).start()

    def _hp(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _hm(self, e):
        if self._drag and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def _hr(self, e):
        self._drag = None

    def _refresh(self):
        try:
            prog = Engine.game_stats.progress
            self._ct_total.setText(f"{prog.chaos_cleared:,}")
            self._ct_session.setText(f"+{prog.chaos_session}")
            self._ct_bosses.setText(str(prog.chaos_bosses))
            lvls = prog.wormhole_lvls
            best = prog.best_worm
            for i, bar in enumerate(self._wh_bars):
                v = lvls[i] if i < len(lvls) else 0
                bar.setRange(0, max(best, 1))
                bar.setValue(v)
                self._wh_vals[i].setText(str(v))
            self._best.setText(f"Best: {prog.best_worm}  ·  Total: {prog.total_worm}")
        except Exception:
            pass

    def retranslate(self): pass
