from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QScrollArea, QSlider, QLineEdit
)
from PySide6.QtCore import Qt, QTimer, QPoint
from src.consts.i18n import set_lang, get_lang
from src.utils import config
from src.utils.session_saver import list_sessions
from src.gui.themes import get_theme_names, get_theme

_lang_cbs: list = []
_theme_cbs: list = []


class SettingsWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self, None,
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint)
        self.setObjectName("SettingsWindow")
        self.setFixedWidth(260)
        self._drag: QPoint | None = None

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        # Titlebar
        self._hdr = QWidget()
        self._hdr.setObjectName("WinHeader")
        self._hdr.setFixedHeight(24)
        hdr_lo = QHBoxLayout(self._hdr)
        hdr_lo.setContentsMargins(8, 0, 6, 0)
        lbl = QLabel("⚙  SETTINGS")
        lbl.setObjectName("WinTitle")
        hdr_lo.addWidget(lbl)
        lo.addWidget(self._hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner.setObjectName("SettingsWindow")
        ilo = QVBoxLayout(inner)
        ilo.setContentsMargins(10, 8, 10, 10)
        ilo.setSpacing(4)
        scroll.setWidget(inner)
        lo.addWidget(scroll)

        # Language
        ilo.addWidget(self._sec("ЯЗЫК / LANGUAGE"))
        lr = QHBoxLayout(); lr.setSpacing(6)
        self._btn_en = self._sbtn("EN")
        self._btn_ru = self._sbtn("RU")
        self._btn_en.setFixedSize(50, 24)
        self._btn_ru.setFixedSize(50, 24)
        self._btn_en.clicked.connect(lambda: self._set_lang("EN"))
        self._btn_ru.clicked.connect(lambda: self._set_lang("RU"))
        lr.addWidget(self._btn_en); lr.addWidget(self._btn_ru); lr.addStretch()
        ilo.addLayout(lr)
        self._update_lang_btns()

        # Theme
        ilo.addWidget(self._sec("ТЕМА / THEME"))
        self._theme_btns: dict[str, QPushButton] = {}
        for key, name_ru, name_en in get_theme_names():
            lang = get_lang()
            b = self._sbtn(name_ru if lang == "RU" else name_en)
            b.clicked.connect(lambda checked=False, k=key: self._set_theme(k))
            self._theme_btns[key] = b
            ilo.addWidget(b)
        self._update_theme_btns()

        # Volume
        ilo.addWidget(self._sec("ГРОМКОСТЬ / VOLUME"))
        vol_row = QHBoxLayout(); vol_row.setSpacing(8)
        self._vol_slider = QSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setObjectName("VolumeSlider")
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(int(config.get("volume") or 80))
        self._vol_label = QLabel(f"{self._vol_slider.value()}%")
        self._vol_label.setObjectName("BDesc")
        self._vol_label.setFixedWidth(32)
        self._vol_slider.valueChanged.connect(self._on_volume)
        vol_row.addWidget(self._vol_slider, 1)
        vol_row.addWidget(self._vol_label)
        ilo.addLayout(vol_row)
        test_btn = self._sbtn("▶ Тест звука")
        test_btn.clicked.connect(self._test_sound)
        ilo.addWidget(test_btn)

        # Notifications
        ilo.addWidget(self._sec("УВЕДОМЛЕНИЯ / NOTIFICATIONS"))
        ilo.addWidget(self._cb("notify_satanic", "Satanic"))
        ilo.addWidget(self._cb("notify_angelic", "Angelic / Unholy"))
        ilo.addWidget(self._cb("notify_heroic",  "Heroic"))

        ilo.addWidget(self._sec("ЗВУК / SOUND"))
        ilo.addWidget(self._cb("sound_enabled", "Звук включён / Sound on"))

        # Mini overlay hotkey
        ilo.addWidget(self._sec("ХОТКЕЙ МИНИ / HOTKEY"))
        hotkey_row = QHBoxLayout(); hotkey_row.setSpacing(6)
        self._hotkey_edit = QLineEdit()
        self._hotkey_edit.setPlaceholderText("Напр: Ctrl+M, F9, Numpad0")
        self._hotkey_edit.setText(config.get("mini_hotkey") or "Ctrl+M")
        self._hotkey_edit.returnPressed.connect(self._save_hotkey)
        hotkey_save = self._sbtn("✓")
        hotkey_save.setFixedWidth(30)
        hotkey_save.clicked.connect(self._save_hotkey)
        hotkey_row.addWidget(self._hotkey_edit, 1)
        hotkey_row.addWidget(hotkey_save)
        ilo.addLayout(hotkey_row)
        self._hotkey_status = QLabel("")
        self._hotkey_status.setObjectName("BDesc")
        ilo.addWidget(self._hotkey_status)

        # Save sessions
        ilo.addWidget(self._sec("СОХРАНЕНИЕ / SESSIONS"))
        ilo.addWidget(self._cb("save_sessions", "Сохранять сессии"))

        # CSV Export
        ilo.addWidget(self._sec("ЭКСПОРТ / EXPORT"))
        export_btn = self._sbtn("📊 Экспорт в CSV")
        export_btn.clicked.connect(self._export_csv)
        ilo.addWidget(export_btn)
        self._export_lbl = QLabel("")
        self._export_lbl.setObjectName("BDesc")
        self._export_lbl.setWordWrap(True)
        ilo.addWidget(self._export_lbl)

        # History
        ilo.addWidget(self._sec("ИСТОРИЯ / HISTORY"))
        self._hist_lo = QVBoxLayout()
        self._hist_lo.setSpacing(2)
        ilo.addLayout(self._hist_lo)
        ilo.addStretch()
        self._load_history()
        QTimer(self, timeout=self._load_history, interval=15000).start()

    def _sec(self, text: str) -> QLabel:
        l = QLabel(text.upper())
        l.setObjectName("WinTitle")
        l.setStyleSheet("margin-top:6px;margin-bottom:2px;")
        return l

    def _sbtn(self, text: str) -> QPushButton:
        b = QPushButton(text)
        b.setObjectName("SettingsBtn")
        b.setFixedHeight(24)
        return b

    def _cb(self, key: str, label: str) -> QCheckBox:
        c = QCheckBox(label)
        c.setObjectName("SettingsCb")
        c.setChecked(bool(config.get(key)))
        c.stateChanged.connect(lambda v, k=key: config.set(k, bool(v)))
        return c

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = None

    def _set_lang(self, lang: str):
        set_lang(lang)
        config.set("lang", lang)
        self._update_lang_btns()
        for cb in _lang_cbs:
            try: cb(lang)
            except Exception: pass

    def _update_lang_btns(self):
        cur = get_lang()
        for btn, lang in ((self._btn_en, "EN"), (self._btn_ru, "RU")):
            btn.setProperty("active", "true" if cur == lang else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _set_theme(self, key: str):
        self._update_theme_btns(key)
        for cb in _theme_cbs:
            try: cb(key)
            except Exception: pass

    def _update_theme_btns(self, active_key: str = None):
        cur = active_key or get_theme()
        for k, b in self._theme_btns.items():
            b.setProperty("active", "true" if k == cur else "false")
            b.style().unpolish(b)
            b.style().polish(b)

    def _on_volume(self, value: int):
        config.set("volume", value)
        self._vol_label.setText(f"{value}%")

    def _test_sound(self):
        from src.utils.sound import play
        play("Satanic", enabled=True)

    def on_lang_changed(self, cb):
        _lang_cbs.append(cb)

    def on_theme_changed(self, cb):
        _theme_cbs.append(cb)

    def _save_hotkey(self):
        key = self._hotkey_edit.text().strip()
        if not key:
            return
        config.set("mini_hotkey", key)
        self._hotkey_status.setText(f"✓ Сохранено: {key}")
        # Уведомляем главное окно
        for cb in _theme_cbs:
            if callable(cb) and hasattr(cb, '__self__') and hasattr(cb.__self__, '_update_hotkey'):
                try: cb.__self__._update_hotkey(key)
                except Exception: pass
        QTimer.singleShot(2000, lambda: self._hotkey_status.setText(""))

    def _export_csv(self):
        try:
            from src.utils.session_saver import export_csv
            path = export_csv()
            if path:
                import os
                os.startfile(os.path.dirname(path))
                self._export_lbl.setText(f"✓ {os.path.basename(path)}")
            else:
                self._export_lbl.setText("Нет сессий для экспорта")
        except Exception as e:
            self._export_lbl.setText(f"Ошибка: {e}")

    def _load_history(self):
        while self._hist_lo.count():
            item = self._hist_lo.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        sessions = list_sessions()
        if not sessions:
            l = QLabel("—"); l.setObjectName("BDesc")
            self._hist_lo.addWidget(l)
        else:
            for s in sessions[:5]:
                ts   = s.get("timestamp", "")[:16].replace("T", " ")
                acc  = s.get("character", {})
                gold = s.get("gold", {}).get("earned", 0)
                dur  = s.get("session", {}).get("duration", "")
                txt  = f"{ts}  {acc.get('name','?')} +{gold:,}g  {dur}"
                l = QLabel(txt); l.setObjectName("BDesc"); l.setWordWrap(True)
                self._hist_lo.addWidget(l)

    def retranslate(self): pass
