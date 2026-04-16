from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QPoint
from src.consts.i18n import t
from src.engine import Engine


def _lbl(txt, w=None, c="#C3AF75", s=11):
    l = QLabel(txt)
    l.setStyleSheet(
        f"color:{c};font-size:{s}px;font-family:'CookieRun Bold';"
        "background:transparent;border:none;")
    if w:
        l.setFixedWidth(w)
    return l


class _ZRow(QWidget):
    def __init__(self, rec, rank, bg, bx, bs, note_cb):
        QWidget.__init__(self)
        self._name = rec.name
        self._cb   = note_cb
        is_best    = (rank == 0)

        if is_best:
            self.setObjectName("ZoneRowBest")
        else:
            self.setObjectName("ZoneRow")

        lo = QVBoxLayout(self)
        lo.setContentsMargins(8, 4, 8, 4)
        lo.setSpacing(2)

        # Row 1: rank + name + time + visits
        r1 = QHBoxLayout(); r1.setSpacing(6)
        r1.addWidget(_lbl(f"#{rank+1}", 22, "#CA1717" if is_best else "#3a2010", 11))
        r1.addWidget(_lbl(rec.name[:30], None, "#F6C94E" if is_best else "#8a7040", 12), 1)
        r1.addWidget(_lbl(f"{rec.minutes():.1f}м", 46, "#4a3010", 10))
        r1.addWidget(_lbl(f"×{rec.visits}", 28, "#3a2010", 9))
        lo.addLayout(r1)

        # Row 2: stats with % comparison
        r2 = QHBoxLayout(); r2.setSpacing(5)

        def pc(val, best):
            if best <= 0: return "#3a2010"
            p = val / best
            return "#CA1717" if p >= 0.9 else ("#C3AF75" if p >= 0.6 else "#3a2010")

        def ps(val, best):
            return f"({int(val/best*100)}%)" if best > 0 else ""

        r2.addWidget(_lbl("G:",   14, "#3a2010", 9))
        r2.addWidget(_lbl(f"{rec.gph():,} {ps(rec.gph(), bg)}/ч",    100, pc(rec.gph(), bg), 11))
        r2.addWidget(_lbl("XP:",  18, "#3a2010", 9))
        r2.addWidget(_lbl(f"{rec.xph():,} {ps(rec.xph(), bx)}/ч",    100, pc(rec.xph(), bx), 11))
        r2.addWidget(_lbl("Сат:", 26, "#3a2010", 9))
        r2.addWidget(_lbl(f"{rec.sat_ph():.1f} {ps(rec.sat_ph(), bs)}/ч", 80, pc(rec.sat_ph(), bs), 11))
        r2.addWidget(_lbl(f"Анг:{rec.ang_ph():.1f}/ч", 70, "#F6F794", 10))
        r2.addStretch()
        lo.addLayout(r2)

        # Row 3: note
        r3 = QHBoxLayout(); r3.setSpacing(4)
        r3.addWidget(_lbl("📝", 16, "#2a1a08", 10))
        existing = "; ".join(n.text for n in rec.notes) if rec.notes else ""
        self._edit = QLineEdit()
        self._edit.setPlaceholderText(t("note_placeholder"))
        self._edit.setFixedHeight(20)
        self._edit.setText(existing)
        self._edit.returnPressed.connect(self._save)
        self._orig_focus_out = self._edit.focusOutEvent
        self._edit.focusOutEvent = self._on_focus_out
        save_btn = QPushButton("✓")
        save_btn.setObjectName("SettingsBtn")
        save_btn.setFixedSize(20, 20)
        save_btn.clicked.connect(self._save)
        r3.addWidget(self._edit)
        r3.addWidget(save_btn)
        lo.addLayout(r3)

    def _on_focus_out(self, e):
        self._orig_focus_out(e)
        self._save()

    def _save(self):
        self._cb(self._name, self._edit.text())


class ZoneWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self, None,
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint)
        self.setObjectName("ZoneWindow")
        self.setFixedWidth(520)
        self._drag_pos: QPoint | None = None

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        # Custom titlebar
        hdr = QWidget()
        hdr.setObjectName("WinHeader")
        hdr.setFixedHeight(26)
        hdr_lo = QHBoxLayout(hdr)
        hdr_lo.setContentsMargins(8, 0, 6, 0)
        hdr_lo.setSpacing(3)

        title = QLabel("ЭФФЕКТИВНОСТЬ ЗОН")
        title.setObjectName("WinTitle")
        hdr_lo.addWidget(title)
        hdr_lo.addStretch()

        self._sort = "score"
        self._sbtns: dict[str, QPushButton] = {}
        for k, lbl in [("score","⭐"),("gph","G/ч"),("xph","XP/ч"),("sat","Сат/ч"),("time","Время")]:
            b = QPushButton(lbl)
            b.setObjectName("SettingsBtn")
            b.setFixedHeight(20)
            b.setProperty("act", "1" if k == self._sort else "0")
            b.clicked.connect(lambda checked=False, key=k: self._set_sort(key))
            self._sbtns[k] = b
            hdr_lo.addWidget(b)
        lo.addWidget(hdr)

        # Drag
        hdr.mousePressEvent   = self._hp
        hdr.mouseMoveEvent    = self._hm
        hdr.mouseReleaseEvent = self._hr

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)

        self._content = QWidget()
        self._content.setObjectName("ZoneWindow")
        self._clo = QVBoxLayout(self._content)
        self._clo.setContentsMargins(0, 0, 0, 0)
        self._clo.setSpacing(0)
        self._scroll.setWidget(self._content)
        lo.addWidget(self._scroll)

        # Summary bar
        self._summary = QLabel("")
        self._summary.setObjectName("BDesc")
        self._summary.setStyleSheet("padding:4px 10px; border-top:1px solid #150a0a;")
        lo.addWidget(self._summary)

        self._last_hash = ""
        QTimer(self, timeout=self._refresh, interval=1000).start()

    def _hp(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _hm(self, e):
        if self._drag_pos and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def _hr(self, e):
        self._drag_pos = None

    def _set_sort(self, key: str):
        self._sort = key
        for k, b in self._sbtns.items():
            b.setProperty("act", "1" if k == key else "0")
            b.style().unpolish(b)
            b.style().polish(b)
        self._refresh(force=True)

    def _note_cb(self, zone: str, text: str):
        Engine.game_stats.zone_eff.add_note(zone, text)

    def _refresh(self, force=False):
        records = Engine.game_stats.zone_eff.sorted_records(self._sort)
        h = str([(r.name, round(r.seconds), r.gold_earned, r.satanic) for r in records])
        if h == self._last_hash and not force:
            return
        self._last_hash = h

        while self._clo.count():
            item = self._clo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not records:
            ph = QLabel(f"  {t('enter_zone')}")
            ph.setWordWrap(True)
            ph.setObjectName("BDesc")
            ph.setStyleSheet("padding:14px 10px;")
            self._clo.addWidget(ph)
            self._summary.setText("")
        else:
            bg = max((r.gph()    for r in records), default=0)
            bx = max((r.xph()    for r in records), default=0)
            bs = max((r.sat_ph() for r in records), default=0.0)
            for i, rec in enumerate(records):
                self._clo.addWidget(_ZRow(rec, i, bg, bx, bs, self._note_cb))

            tm   = sum(r.minutes() for r in records)
            ts   = sum(r.satanic   for r in records)
            ta   = sum(r.angelic   for r in records)
            best = records[0]
            self._summary.setText(
                f"Зон:{len(records)}  Время:{tm:.0f}м  "
                f"Сат:{ts}  Анг:{ta}  Лучшая:{best.name[:20]}")

        self._clo.addStretch()
        self.setMinimumHeight(min(max(len(records) * 90 + 80, 120), 520))
        self.adjustSize()

    def retranslate(self):
        pass
