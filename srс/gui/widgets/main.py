"""
MainWidget v10 — главное окно Hero Siege Stats.
Frameless, Always-on-top, перетаскивается.
При сворачивании/разворачивании секций вызывает resize(sizeHint())
чтобы окно реально сжималось без пустых мест.
"""
from PySide6.QtCore import Qt, QTimer, QPoint, QUrl
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from PySide6.QtGui import QDesktopServices

from src.gui.layouts.stats import StatsLayout
from src.gui.widgets.toast import ToastWidget
from src.gui.windows.drop_log_window import DropLogWindow
from src.gui.windows.zone_window import ZoneWindow
from src.gui.windows.settings_window import SettingsWindow
from src.gui.windows.faq_window import FaqWindow
from src.engine import Engine
from src.consts.i18n import t, set_lang
from src.utils import config, session_saver
from src.utils.sound import play as play_sound

_TB  = "QWidget{background:#0a0707;border-bottom:1px solid #140d0d;}"
_B   = ("QPushButton{background:#0a0707;border:none;border-left:1px solid #150d0d;"
        "color:#3a2010;font-size:10px;padding:0 7px;min-height:22px;}"
        "QPushButton:hover{background:#120a0a;color:#C3AF75;}"
        "QPushButton:checked{background:#160808;color:#CA1717;}")
_BD  = ("QPushButton{background:#0a0707;border:none;border-left:1px solid #150d0d;"
        "color:#2a3050;font-size:10px;padding:0 7px;min-height:22px;}"
        "QPushButton:hover{background:#0a0d18;color:#6070D0;}")
_BC  = ("QPushButton{background:#0a0707;border:none;border-left:1px solid #150d0d;"
        "color:#200e0e;font-size:11px;min-width:22px;min-height:22px;}"
        "QPushButton:hover{background:#150505;color:#CA1717;}")


class MainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self, None,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("MainWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)

        config.load()
        set_lang(config.get("lang") or "EN")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Тулбар ─────────────────────────────────────────────────
        tb = QWidget()
        tb.setFixedHeight(22)
        tb.setStyleSheet(_TB)
        tbl = QHBoxLayout(tb)
        tbl.setContentsMargins(0, 0, 0, 0)
        tbl.setSpacing(0)

        self._b_drops = self._mkbtn("Дропы")
        self._b_zones = self._mkbtn("Зоны")
        self._b_set   = self._mkbtn("⚙")
        self._b_faq   = self._mkbtn("?")

        b_disc = QPushButton("Discord")
        b_disc.setStyleSheet(_BD)
        b_disc.setFixedHeight(22)
        b_disc.setToolTip("discord.gg/SjkJM6nv")
        b_disc.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://discord.gg/SjkJM6nv")))

        b_close = QPushButton("✕")
        b_close.setStyleSheet(_BC)
        b_close.setFixedSize(22, 22)
        b_close.clicked.connect(self._on_close)

        tbl.addStretch()
        for w in (self._b_drops, self._b_zones, self._b_set, self._b_faq, b_disc, b_close):
            tbl.addWidget(w)
        root.addWidget(tb)

        # ── StatsLayout ─────────────────────────────────────────────
        self.view = StatsLayout()
        root.addWidget(self.view)

        # ── Подключаем пересчёт размера к каждой секции ────────────
        for sec in (self.view._s_gold, self.view._s_xp,
                    self.view._s_items, self.view._s_zone, self.view._s_ct):
            sec.toggled.connect(self._relayout)

        # ── Дочерние окна ───────────────────────────────────────────
        self._dw = DropLogWindow()
        self._zw = ZoneWindow()
        self._sw = SettingsWindow()
        self._fw = FaqWindow()
        self._toast = ToastWidget()

        self._b_drops.clicked.connect(lambda c: self._toggle_win(self._dw, self._b_drops, c))
        self._b_zones.clicked.connect(lambda c: self._toggle_win(self._zw, self._b_zones, c))
        self._b_set.clicked.connect(  lambda c: self._toggle_win(self._sw, self._b_set,   c))
        self._b_faq.clicked.connect(  lambda c: self._toggle_win(self._fw, self._b_faq,   c))

        self._sw.on_lang_changed(self._on_lang)
        Engine.game_stats.drop_log.on_notable_drop(self._on_drop)
        Engine.game_stats.on_mail(self._on_mail)

        QTimer(self, timeout=self.view.refresh, interval=500).start()

        self._drag: QPoint | None = None
        self._restore_pos()

    # ── Кнопка тулбара ──────────────────────────────────────────────
    def _mkbtn(self, text: str) -> QPushButton:
        b = QPushButton(text)
        b.setCheckable(True)
        b.setFixedHeight(22)
        b.setStyleSheet(_B)
        return b

    # ── Пересчёт размера при toggle секций ──────────────────────────
    def _relayout(self) -> None:
        """
        Единственный надёжный способ сжать frameless окно в Qt:
        1. Обновляем геометрию layout
        2. Вызываем resize(sizeHint()) — пересчитывает по актуальному содержимому
        """
        self.view.updateGeometry()
        # QTimer.singleShot нужен чтобы Qt завершил hide/show виджета ДО resize
        QTimer.singleShot(0, self._do_resize)

    def _do_resize(self) -> None:
        hint = self.view.sizeHint()
        # 22 = высота тулбара
        self.resize(hint.width(), hint.height() + 22)

    # ── Drag ─────────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = None
            p = self.pos()
            config.set("win_main", {"x": p.x(), "y": p.y()})

    # ── Позиция ──────────────────────────────────────────────────────
    def _restore_pos(self) -> None:
        from PySide6.QtWidgets import QApplication
        scr = QApplication.primaryScreen().geometry()
        pos = config.get("win_main")
        if pos and pos.get("x", -1) >= 0:
            x = max(0, min(pos["x"], scr.width()  - 200))
            y = max(0, min(pos["y"], scr.height() - 100))
            self.move(x, y)
        else:
            self.move(scr.width() - 400, scr.height() - 450)

    # ── Дочерние окна ────────────────────────────────────────────────
    def _toggle_win(self, win: QWidget, btn: QPushButton, checked: bool) -> None:
        if checked:
            p = self.pos()
            win.move(p.x() + self.width() + 5, p.y())
            win.show()
            win.raise_()
        else:
            win.hide()

    # ── Drop notification ─────────────────────────────────────────────
    def _on_drop(self, entry) -> None:
        key = {
            "Satanic": "notify_satanic",
            "Angelic": "notify_angelic",
            "Unholy":  "notify_angelic",
            "Heroic":  "notify_heroic",
        }.get(entry.rarity)
        if key and not config.get(key):
            return
        rarity = entry.rarity.lower()
        valid_keys = {"satanic", "angelic", "unholy", "heroic"}
        toast_key = f"toast_{rarity}" if rarity in valid_keys else "toast_satanic"
        QTimer.singleShot(0, lambda: self._toast.show_drop(entry.rarity, t(toast_key)))
        if config.get("sound_enabled"):
            play_sound(entry.rarity, enabled=True)

    # ── Mail notification ─────────────────────────────────────────────
    def _on_mail(self) -> None:
        if config.get("sound_enabled"):
            play_sound("Mail", enabled=True)
        QTimer.singleShot(0, lambda: self._toast.show_drop("Mail", t("toast_mail")))

    # ── Language ──────────────────────────────────────────────────────
    def _on_lang(self, lang: str) -> None:
        self.view.retranslate()
        for w in (self._dw, self._zw, self._sw, self._fw):
            try:
                w.retranslate()
            except Exception:
                pass
        Engine.game_stats.account.retranslate()

    # ── Close ─────────────────────────────────────────────────────────
    def _on_close(self) -> None:
        if config.get("save_sessions"):
            try:
                session_saver.save_session(Engine.get_stats())
            except Exception:
                pass
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
