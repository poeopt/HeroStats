import datetime
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QApplication
)
from PySide6.QtCore import Qt, QTimer

from src.gui.components.value_display import ValueDisplay
from src.gui.components.zone_panel import ZonePanel
from src.gui.components.collapsible import CollapsibleSection
from src.gui.components.progress_panel import ProgressPanel

from src.models.stats.stats import Stats
from src.engine import Engine
from src.consts import assets as fc
from src.consts.enums import Sizes

_GOLD    = "#C3AF75"
_ANGELIC = "#F6F794"
_HEROIC  = "#00FFAE"
_SATANIC = "#CA1717"
_MF      = "#4040A0"


def _c(col: str, txt: str) -> str:
    return f'<font color="{col}">{txt}</font>'


class _Row(QWidget):
    def __init__(self, *widgets):
        QWidget.__init__(self)
        lo = QHBoxLayout(self)
        lo.setContentsMargins(6, 0, 6, 0)
        lo.setSpacing(3)
        for w in widgets: lo.addWidget(w)
        lo.addStretch()


# ── Character card ────────────────────────────────────────────────────
class CharacterCard(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setFixedHeight(36)
        self.setStyleSheet("background:#0a0707;border-bottom:1px solid #150e0e;")

        lo = QHBoxLayout(self)
        lo.setContentsMargins(10, 0, 8, 0)
        lo.setSpacing(8)

        info = QVBoxLayout(); info.setSpacing(0); info.setContentsMargins(0,0,0,0)
        self._class = QLabel("—")
        self._class.setStyleSheet("color:#5a3a20;font-size:9px;font-family:'CookieRun Bold';background:transparent;")
        self._name  = QLabel("Waiting for game...")
        self._name.setStyleSheet("color:#C3AF75;font-size:13px;font-family:'CookieRun Bold';background:transparent;")
        info.addWidget(self._class)
        info.addWidget(self._name)
        lo.addLayout(info)

        self._lvl = QLabel("")
        self._lvl.setStyleSheet("color:#4a3520;font-size:10px;font-family:'CookieRun Bold';background:transparent;")
        lo.addWidget(self._lvl)
        lo.addStretch()

        self._mode_badge = self._badge("—", "#151010", "#5a3020")
        self._diff_badge = self._badge("—", "#151010", "#5a3020")
        lo.addWidget(self._mode_badge)
        lo.addWidget(self._diff_badge)

    def _badge(self, txt, bg, fg) -> QLabel:
        l = QLabel(txt)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setMinimumWidth(60)
        l.setStyleSheet(
            f"background:{bg};color:{fg};border:1px solid {fg}44;"
            "border-radius:3px;font-size:10px;font-family:'CookieRun Bold';padding:1px 6px;")
        return l

    _MODE_STYLE = {
        "GSS": ("#0a1e12","#00FFAE"), "GSH": ("#1e0a0a","#CA1717"),
        "GNS": ("#0a121e","#4a90C0"), "GNH": ("#120a1e","#A050C0"),
        "GBP": ("#1a150a","#C3AF75"),
    }
    _DIFF_STYLE = {
        0: ("#0a150a","#50A030"), 1: ("#150f0a","#C07030"), 2: ("#150a0a","#CA1717"),
    }

    def update_account(self, acc) -> None:
        if acc.class_id == -1:
            return
        from src.consts.i18n import get_lang
        lang = get_lang()
        self._class.setText(acc.class_name.upper())
        self._name.setText(acc.name)
        hero = f"  ·  Hero {acc.hero_level}" if acc.hero_level else ""
        self._lvl.setText(f"Lv.{acc.level}{hero}")

        mb, mf = self._MODE_STYLE.get(acc.mode, ("#151010","#5a3020"))
        self._mode_badge.setText(acc.mode_label)
        self._mode_badge.setStyleSheet(
            f"background:{mb};color:{mf};border:1px solid {mf}44;"
            "border-radius:3px;font-size:10px;font-family:'CookieRun Bold';padding:1px 6px;")

        db, df = self._DIFF_STYLE.get(acc.difficulty, ("#151010","#5a3020"))
        self._diff_badge.setText(acc.diff_label)
        self._diff_badge.setStyleSheet(
            f"background:{db};color:{df};border:1px solid {df}44;"
            "border-radius:3px;font-size:10px;font-family:'CookieRun Bold';padding:1px 6px;")


# ── Session row ───────────────────────────────────────────────────────
class SessionRow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setStyleSheet("background:#181212;border-bottom:1px solid #150e0e;")
        lo = QHBoxLayout(self)
        lo.setContentsMargins(6, 2, 6, 2)
        lo.setSpacing(3)

        self._dur  = ValueDisplay(icon=fc.IcTime, value="0:00:00",
                                  size=Sizes.Large)
        self._mail = QLabel("—")
        self._mail.setObjectName("MailInactive")
        self._mail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mail.setFixedWidth(52)

        self._death = QLabel("")
        self._death.setStyleSheet(
            "color:#CA1717;font-size:10px;font-family:'CookieRun Bold';"
            "background:transparent;border:none;")
        self._death.setToolTip("Смертей за сессию")
        self._death.hide()

        self._copy = QPushButton("⎘")
        self._copy.setObjectName("CopyButton")
        self._copy.setFixedSize(26, 26)
        self._copy.setToolTip("Копировать статистику")
        self._copy.clicked.connect(self._do_copy)

        self._reset = QPushButton("Reset")
        self._reset.setObjectName("ResetButton")
        self._reset.setFixedSize(52, 26)
        self._reset.clicked.connect(Engine.reset_stats)

        lo.addWidget(self._dur)
        lo.addWidget(self._mail)
        lo.addWidget(self._death)
        lo.addStretch()
        lo.addWidget(self._copy)
        lo.addWidget(self._reset)

        self._had_mail = False
        self._blink_v  = True
        self._btimer = QTimer(self)
        self._btimer.timeout.connect(self._blink)

    def _blink(self):
        self._blink_v = not self._blink_v
        self._mail.setVisible(self._blink_v)

    def _do_copy(self):
        QApplication.clipboard().setText(_format_text(Engine.get_stats()))
        self._copy.setText("✓")
        QTimer.singleShot(1500, lambda: self._copy.setText("⎘"))

    def update(self, session, death_count: int = 0):
        self._dur.setValue(session.get_duration_str())
        if death_count > 0:
            self._death.setText(f"☠ {death_count}")
            self._death.show()
        else:
            self._death.hide()
        if session.has_mail != self._had_mail:
            self._had_mail = session.has_mail
            if session.has_mail:
                self._mail.setObjectName("MailActive")
                self._mail.setText("Mail!")
                self._btimer.start(600)
            else:
                self._btimer.stop()
                self._mail.setVisible(True)
                self._mail.setObjectName("MailInactive")
                self._mail.setText("—")
            self._mail.style().unpolish(self._mail)
            self._mail.style().polish(self._mail)


def _format_text(stats: Stats) -> str:
    acc   = stats.account
    prog  = stats.progress
    items = stats.added_items.added_items
    ph    = stats.added_items.items_per_hour
    ang_t = items['Angelic']['total'] + items['Unholy']['total']
    ang_m = items['Angelic']['mf']    + items['Unholy']['mf']
    lines = [f"Hero Siege Stats  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    if acc.class_id != -1:
        lines.append(f"{acc.class_name} {acc.name}  Lv.{acc.level} Hero {acc.hero_level}  {acc.mode_label} {acc.diff_label}")
    lines += [
        f"Session: {stats.session.get_duration_str()}  Deaths: {stats.death_count}",
        f"Gold:  {stats.gold.total_gold:,}  +{stats.gold.total_gold_earned:,}  {stats.gold.gold_per_hour:,}/h",
        f"XP:    {stats.xp.total_xp:,}  +{stats.xp.total_xp_earned:,}  {stats.xp.xp_per_hour:,}/h",
        f"Angelic/Unholy: {ang_t} (MF:{ang_m})",
        f"Heroic:  {items['Heroic']['total']} (MF:{items['Heroic']['mf']}) {ph.get('Heroic',0)}/h",
        f"Satanic: {items['Satanic']['total']} (MF:{items['Satanic']['mf']}) {ph.get('Satanic',0)}/h",
        f"Chaos: {prog.chaos_cleared} (+{prog.chaos_session} session)  Bosses: {prog.chaos_bosses}",
        f"Wormhole: best {prog.best_worm}  total {prog.total_worm}",
    ]
    if stats.satanic_zone.satanic_zone_info:
        z = stats.satanic_zone.satanic_zone_info
        lines.append(f"Zone: {z.satanic_zone}")
        for b in z.buffs:
            lines.append(f"  · {b.buff_name}")
    return "\n".join(lines)


# ── Main Layout ───────────────────────────────────────────────────────
class StatsLayout(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName("InnerWidget")

        lo = QVBoxLayout(self)
        lo.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        lo.setSpacing(0)
        lo.setContentsMargins(0, 0, 0, 0)

        self.char_card = CharacterCard()
        lo.addWidget(self.char_card)

        self.session_row = SessionRow()
        lo.addWidget(self.session_row)

        # Gold
        self._s_gold = CollapsibleSection("Gold", "gold", True)
        self._g0 = ValueDisplay(icon=fc.IcCoins, value="0")
        self._g1 = ValueDisplay(value="+0", size=Sizes.Medium)
        self._g2 = ValueDisplay(value="0/h",size=Sizes.Medium)
        self._s_gold.add_widget(_Row(self._g0, self._g1, self._g2))
        lo.addWidget(self._s_gold)

        # XP
        self._s_xp = CollapsibleSection("Experience", "xp", True)
        self._x0 = ValueDisplay(icon=fc.IcXp, value="0")
        self._x1 = ValueDisplay(value="+0", size=Sizes.Medium)
        self._x2 = ValueDisplay(value="0/h",size=Sizes.Medium)
        self._s_xp.add_widget(_Row(self._x0, self._x1, self._x2))
        lo.addWidget(self._s_xp)

        # Items
        self._s_items = CollapsibleSection("Angelic · Heroic · Satanic", "items", True)
        self._a0 = ValueDisplay(icon=fc.IcChest, value="0(0)")
        self._a1 = ValueDisplay(value="0|0/h", size=Sizes.Medium)
        self._a2 = ValueDisplay(value="0|0/h", size=Sizes.Medium)
        self._h0 = ValueDisplay(icon=fc.IcChest, value="0(0)")
        self._h1 = ValueDisplay(value="0|0/h", size=Sizes.Medium)
        self._h2 = ValueDisplay(value="0|0/h", size=Sizes.Medium)
        self._S0 = ValueDisplay(icon=fc.IcChest, value="0(0)")
        self._S1 = ValueDisplay(value="0|0/h", size=Sizes.Medium)
        self._S2 = ValueDisplay(value="0|0/h", size=Sizes.Medium)
        self._s_items.add_widget(_Row(self._a0, self._a1, self._a2))
        self._s_items.add_widget(_Row(self._h0, self._h1, self._h2))
        self._s_items.add_widget(_Row(self._S0, self._S1, self._S2))
        lo.addWidget(self._s_items)

        # Zone
        self._s_zone = CollapsibleSection("Satanic Zone", "zone", True)
        self.zone_panel = ZonePanel()
        self._s_zone.add_widget(self.zone_panel)
        lo.addWidget(self._s_zone)

        # Chaos Tower
        self._s_ct = CollapsibleSection("Chaos Tower", "chaos", False)
        self.progress = ProgressPanel()
        self._s_ct.add_widget(self.progress)
        lo.addWidget(self._s_ct)

    def _ir(self, col, t, m, r, total, mf, ph):
        c, cm = col, _MF
        v = (f'{_c(c,str(total))} {_c(cm,f"({mf})")} '
             f'{_c("#3a2010","|")} {_c(c,f"{ph}/h")}')
        t.setValue(f'{_c(c,str(total))} {_c(cm,f"({mf})")}')
        m.setValue(v); r.setValue(v)

    def update_stats(self, stats: Stats):
        self.char_card.update_account(stats.account)
        self.session_row.update(stats.session, stats.death_count)

        g = stats.gold
        self._g0.setValue(_c(_GOLD, f"{g.total_gold:,}"))
        self._g1.setValue(_c(_GOLD, f"+{g.total_gold_earned:,}"))
        self._g2.setValue(_c(_GOLD, f"{g.gold_per_hour:,}/h"))

        x = stats.xp
        self._x0.setValue(_c(_GOLD, f"{x.total_xp:,}"))
        self._x1.setValue(_c(_GOLD, f"+{x.total_xp_earned:,}"))
        self._x2.setValue(_c(_GOLD, f"{x.xp_per_hour:,}/h"))

        items = stats.added_items.added_items
        ph    = stats.added_items.items_per_hour
        at = items['Angelic']['total'] + items['Unholy']['total']
        am = items['Angelic']['mf']    + items['Unholy']['mf']
        ah = ph.get('Angelic',0) + ph.get('Unholy',0)
        self._ir(_ANGELIC, self._a0, self._a1, self._a2, at, am, ah)
        self._ir(_HEROIC,  self._h0, self._h1, self._h2,
                 items['Heroic']['total'],  items['Heroic']['mf'],  ph.get('Heroic',0))
        self._ir(_SATANIC, self._S0, self._S1, self._S2,
                 items['Satanic']['total'], items['Satanic']['mf'], ph.get('Satanic',0))

        self.zone_panel.update_zone(stats.satanic_zone.satanic_zone_info)
        self.progress.update_progress(stats.progress)

    def refresh(self):
        self.update_stats(Engine.get_stats())

    def retranslate(self):
        self.zone_panel.retranslate()
