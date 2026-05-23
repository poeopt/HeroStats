"""MainWidget — главное окно Hero Siege Stats."""
from PySide6.QtCore import Qt, QTimer, QPoint, QUrl
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QApplication
from PySide6.QtGui import QDesktopServices

from src.gui.layouts.stats import StatsLayout
from src.gui.widgets.toast import ToastWidget
from src.gui.windows.drop_log_window import DropLogWindow
from src.gui.windows.zone_window import ZoneWindow
from src.gui.windows.chaos_window import ChaosWindow
from src.gui.windows.settings_window import SettingsWindow
from src.gui.windows.faq_window import FaqWindow
from src.gui.windows.mini_overlay import MiniOverlay
from PySide6.QtGui import QShortcut, QKeySequence
from src.gui.themes import build_style, set_theme
from src.engine import Engine
from src.consts.i18n import t, set_lang
from src.utils import config, session_saver
from src.utils.sound import play as play_sound


def _apply_theme(theme_key: str) -> None:
    set_theme(theme_key)
    config.set("theme", theme_key)
    QApplication.instance().setStyleSheet(build_style(theme_key))


class MainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self, None,
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("MainWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)

        config.load()
        set_lang(config.get("lang") or "EN")
        _apply_theme(config.get("theme") or "dark")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Тулбар ─────────────────────────────────────────────
        tb = QWidget()
        tb.setObjectName("Toolbar")
        tb.setFixedHeight(22)
        tbl = QHBoxLayout(tb)
        tbl.setContentsMargins(0, 0, 0, 0)
        tbl.setSpacing(0)

        self._b_drops = self._tbtn("Дропы")
        self._b_zones = self._tbtn("Зоны")
        self._b_chaos = self._tbtn("Башня")
        self._b_set   = self._tbtn("⚙")
        self._b_faq   = self._tbtn("?")

        b_disc = QPushButton("Discord")
        b_disc.setObjectName("TbBtnDiscord")
        b_disc.setFixedHeight(22)
        b_disc.setToolTip("discord.gg/SjkJM6nv")
        b_disc.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://discord.gg/SjkJM6nv")))

        # Mini overlay кнопка
        b_mini = QPushButton("◉")
        b_mini.setObjectName("TbBtnMin")
        b_mini.setFixedSize(22, 22)
        b_mini.setToolTip("Mini overlay (компактный режим)")
        b_mini.setCheckable(True)
        b_mini.clicked.connect(lambda c: self._toggle_mini(c))

        b_min = QPushButton("—")
        b_min.setObjectName("TbBtnMin")
        b_min.setFixedSize(22, 22)
        b_min.setToolTip("Свернуть")
        b_min.clicked.connect(self.showMinimized)

        b_close = QPushButton("✕")
        b_close.setObjectName("TbBtnClose")
        b_close.setFixedSize(22, 22)
        b_close.clicked.connect(self._on_close)

        tbl.addStretch()
        for w in (self._b_drops, self._b_zones, self._b_chaos,
                  self._b_set, self._b_faq, b_disc, b_mini, b_min, b_close):
            tbl.addWidget(w)
        root.addWidget(tb)

        # ── Stats layout ────────────────────────────────────────
        self.view = StatsLayout()
        root.addWidget(self.view)

        for sec in (self.view._s_gold, self.view._s_xp,
                    self.view._s_items, self.view._s_zone):
            sec.toggled.connect(self._relayout)

        # ── Child windows ───────────────────────────────────────
        self._dw   = DropLogWindow()
        self._zw   = ZoneWindow()
        self._cw   = ChaosWindow()
        self._sw   = SettingsWindow()
        self._fw   = FaqWindow()
        self._mo   = MiniOverlay(on_expand=self._expand_from_mini)
        self._toast = ToastWidget()
        self._mini_active = False

        # Глобальный хоткей Ctrl+M — toggle mini overlay
        hotkey = config.get("mini_hotkey") or "Ctrl+M"
        self._mini_shortcut = QShortcut(QKeySequence(hotkey), self)
        self._mini_shortcut.activated.connect(self._toggle_mini_hotkey)

        self._b_drops.clicked.connect(lambda c: self._toggle_win(self._dw, self._b_drops, c))
        self._b_zones.clicked.connect(lambda c: self._toggle_win(self._zw, self._b_zones, c))
        self._b_chaos.clicked.connect(lambda c: self._toggle_win(self._cw, self._b_chaos, c))
        self._b_set.clicked.connect(  lambda c: self._toggle_win(self._sw, self._b_set,   c))
        self._b_faq.clicked.connect(  lambda c: self._toggle_win(self._fw, self._b_faq,   c))

        self._sw.on_lang_changed(self._on_lang)
        self._sw.on_theme_changed(_apply_theme)

        Engine.game_stats.drop_log.on_notable_drop(self._on_drop)
        Engine.game_stats.on_mail(self._on_mail)

        QTimer(self, timeout=self.view.refresh, interval=500).start()
        self._drag: QPoint | None = None
        self._restore_pos()

    def _tbtn(self, text: str) -> QPushButton:
        b = QPushButton(text)
        b.setObjectName("TbBtn")
        b.setCheckable(True)
        b.setFixedHeight(22)
        return b

    # ── Resize ──────────────────────────────────────────────────
    def _relayout(self) -> None:
        self.view.layout().activate()
        self.view.updateGeometry()
        QTimer.singleShot(1, self._do_resize)

    def _do_resize(self) -> None:
        self.view.layout().activate()
        hint = self.view.sizeHint()
        new_h = hint.height() + 22
        if self.height() != new_h:
            self.resize(hint.width(), new_h)

    # ── Mini overlay ─────────────────────────────────────────────
    def _update_hotkey(self, new_key: str) -> None:
        """Перерегистрирует хоткей mini overlay."""
        try:
            self._mini_shortcut.setKey(QKeySequence(new_key))
        except Exception:
            pass

    def _toggle_mini_hotkey(self) -> None:
        """Хоткей Ctrl+M — переключает mini overlay."""
        if self._mini_active:
            self._expand_from_mini()
        else:
            self._toggle_mini(True)

    def _toggle_mini(self, checked: bool) -> None:
        if checked:
            # Показываем mini overlay, прячем главное окно
            p = self.pos()
            self._mo.move(p.x(), p.y())
            self._mo.show()
            self._mo.raise_()
            self.hide()
            self._mini_active = True
        else:
            self._expand_from_mini()

    def _expand_from_mini(self) -> None:
        self._mo.hide()
        self._mini_active = False

        # Глобальный хоткей Ctrl+M — toggle mini overlay
        hotkey = config.get("mini_hotkey") or "Ctrl+M"
        self._mini_shortcut = QShortcut(QKeySequence(hotkey), self)
        self._mini_shortcut.activated.connect(self._toggle_mini_hotkey)
        self.show()
        self.raise_()

    # ── Drag ────────────────────────────────────────────────────
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

    def _restore_pos(self) -> None:
        scr = QApplication.primaryScreen().geometry()
        pos = config.get("win_main")
        if pos and pos.get("x", -1) >= 0:
            x = max(0, min(pos["x"], scr.width()  - 200))
            y = max(0, min(pos["y"], scr.height() - 100))
            self.move(x, y)
        else:
            self.move(scr.width() - 400, scr.height() - 450)

    def _toggle_win(self, win: QWidget, btn: QPushButton, checked: bool) -> None:
        if checked:
            p = self.pos()
            win.move(p.x() + self.width() + 5, p.y())
            win.show(); win.raise_()
        else:
            win.hide()

    # ── Notifications ────────────────────────────────────────────
    def _on_drop(self, entry) -> None:
        notify_map = {
            "Satanic": "notify_satanic", "Angelic": "notify_angelic",
            "Unholy":  "notify_angelic", "Heroic":  "notify_heroic",
        }
        # Звук для ЛЮБОГО редкого дропа (если включён)
        if config.get("sound_enabled"):
            play_sound(entry.rarity, enabled=True)

        # Toast только для настроенных редкостей
        key = notify_map.get(entry.rarity)
        if key and not config.get(key):
            return
        rarity = entry.rarity.lower()
        valid_toast = {"satanic", "angelic", "unholy", "heroic"}
        if rarity in valid_toast:
            toast_key = f"toast_{rarity}"
            QTimer.singleShot(0, lambda r=entry.rarity, k=toast_key: self._toast.show_drop(r, t(k)))

    def _on_mail(self) -> None:
        if config.get("sound_enabled"):
            play_sound("Mail", enabled=True)
        QTimer.singleShot(0, lambda: self._toast.show_drop("Mail", t("toast_mail")))

    # ── Lang / theme ─────────────────────────────────────────────
    def _on_lang(self, lang: str) -> None:
        self.view.retranslate()
        for w in (self._dw, self._zw, self._cw, self._sw, self._fw):
            try: w.retranslate()
            except Exception: pass
        Engine.game_stats.account.retranslate()

    # ── Close ────────────────────────────────────────────────────
    def _on_close(self) -> None:
        if config.get("save_sessions"):
            try: session_saver.save_session(Engine.get_stats())
            except Exception: pass
        QApplication.quit()
