from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
)
from PySide6.QtCore import Qt

_ACT_COLORS = [
    "#CA1717","#C07030","#90A030","#30A060",
    "#3080C0","#9030C0","#C03080","#707070",
]
_STYLE_CT = """
QWidget#CTPanel { background:#0f0808; border-bottom:1px solid #1a0e0e; }
QLabel { color:#7a5030; font-family:"CookieRun Bold"; font-size:10px; }
QLabel#CTVal { color:#C3AF75; }
"""
_STYLE_WH = """
QWidget#WHPanel { background:#0a0808; }
QLabel { color:#5a4020; font-family:"CookieRun Bold"; font-size:9px; }
QProgressBar {
    background:#0f0808; border:none; border-radius:1px;
    max-height:5px; text-visible:0;
}
"""


def _wh_bar(color: str, value: int, max_val: int = 10) -> QProgressBar:
    bar = QProgressBar()
    bar.setRange(0, max(max_val, 1))
    bar.setValue(min(value, max_val))
    bar.setTextVisible(False)
    bar.setFixedHeight(5)
    bar.setStyleSheet(
        f"QProgressBar{{background:#0f0808;border:none;border-radius:1px;}}"
        f"QProgressBar::chunk{{background:{color};border-radius:1px;}}"
    )
    return bar


class ProgressPanel(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        # Chaos Tower
        ct = QWidget()
        ct.setObjectName("CTPanel")
        ct.setStyleSheet(_STYLE_CT)
        ct_lo = QVBoxLayout(ct)
        ct_lo.setContentsMargins(8, 5, 8, 5)
        ct_lo.setSpacing(2)

        row1 = QHBoxLayout()
        self._ct_total = QLabel("Total cleared:")
        self._ct_total_val = QLabel("0")
        self._ct_total_val.setObjectName("CTVal")
        row1.addWidget(self._ct_total)
        row1.addWidget(self._ct_total_val)
        row1.addStretch()
        ct_lo.addLayout(row1)

        row2 = QHBoxLayout()
        self._ct_sess = QLabel("This session:")
        self._ct_sess_val = QLabel("+0")
        self._ct_sess_val.setObjectName("CTVal")
        row2.addWidget(self._ct_sess)
        row2.addWidget(self._ct_sess_val)
        row2.addStretch()
        ct_lo.addLayout(row2)

        row3 = QHBoxLayout()
        self._ct_boss = QLabel("Boss kills:")
        self._ct_boss_val = QLabel("0")
        self._ct_boss_val.setObjectName("CTVal")
        row3.addWidget(self._ct_boss)
        row3.addWidget(self._ct_boss_val)
        row3.addStretch()
        ct_lo.addLayout(row3)

        lo.addWidget(ct)

        # Wormhole
        wh = QWidget()
        wh.setObjectName("WHPanel")
        wh.setStyleSheet(_STYLE_WH)
        wh_lo = QVBoxLayout(wh)
        wh_lo.setContentsMargins(8, 5, 8, 5)
        wh_lo.setSpacing(3)

        hdr = QLabel("WORMHOLE LEVELS")
        hdr.setStyleSheet("color:#3a2a10; font-size:9px; letter-spacing:1px;")
        wh_lo.addWidget(hdr)

        grid = QHBoxLayout()
        grid.setSpacing(8)
        self._wh_bars = []
        self._wh_lbls = []

        col1 = QVBoxLayout(); col1.setSpacing(2)
        col2 = QVBoxLayout(); col2.setSpacing(2)
        for i in range(8):
            c = _ACT_COLORS[i]
            row = QHBoxLayout(); row.setSpacing(4)
            lbl = QLabel(f"A{i+1}")
            lbl.setFixedWidth(16)
            lbl.setStyleSheet(f"color:{c}; font-size:9px;")
            bar = _wh_bar(c, 0)
            val = QLabel("0")
            val.setFixedWidth(16)
            val.setStyleSheet(f"color:{c}; font-size:9px;")
            row.addWidget(lbl); row.addWidget(bar, 1); row.addWidget(val)
            self._wh_bars.append(bar)
            self._wh_lbls.append(val)
            if i < 4:
                col1.addLayout(row)
            else:
                col2.addLayout(row)

        grid.addLayout(col1, 1)
        grid.addLayout(col2, 1)
        wh_lo.addLayout(grid)

        best_row = QHBoxLayout()
        self._wh_best = QLabel("Best: 0  ·  Total: 0")
        self._wh_best.setStyleSheet("color:#5a4020; font-size:9px;")
        best_row.addWidget(self._wh_best)
        wh_lo.addLayout(best_row)

        lo.addWidget(wh)

    def update_progress(self, prog) -> None:
        self._ct_total_val.setText(f"{prog.chaos_cleared:,}")
        self._ct_sess_val.setText(f"+{prog.chaos_session}")
        self._ct_boss_val.setText(str(prog.chaos_bosses))
        lvls = prog.wormhole_lvls
        best = prog.best_worm
        for i, bar in enumerate(self._wh_bars):
            v = lvls[i] if i < len(lvls) else 0
            bar.setRange(0, max(best, 1))
            bar.setValue(v)
            self._wh_lbls[i].setText(str(v))
        self._wh_best.setText(f"Best: {prog.best_worm}  ·  Total: {prog.total_worm}")
