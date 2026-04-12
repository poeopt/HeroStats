from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt
from src.consts.i18n import t, set_lang, get_lang
from src.utils import config
from src.utils.session_saver import list_sessions

_WIN = "QWidget { background:#181212; }"
_BTN = ("QPushButton{background:#0f0808;border:1px solid #2a1010;"
        "color:#5a3020;font-size:10px;padding:2px 10px;border-radius:2px;}"
        "QPushButton:hover{color:#C3AF75;border-color:#C3AF75;}")
_ACTIVE = ("QPushButton{background:#1a0505;border:2px solid #CA1717;"
           "color:#CA1717;font-size:10px;padding:2px 10px;border-radius:2px;}")
_CB = ("QCheckBox{color:#8a6040;font-size:11px;spacing:6px;"
       "font-family:'CookieRun Bold';background:transparent;}"
       "QCheckBox::indicator{width:13px;height:13px;border:1px solid #3a1414;"
       "background:#0f0808;border-radius:2px;}"
       "QCheckBox::indicator:checked{background:#7a1a1a;border-color:#CA1717;}")
_SEC = "color:#3a1a10;font-size:9px;letter-spacing:1px;font-family:'CookieRun Bold';background:transparent;"

_lang_cbs: list = []


class SettingsWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self, None,
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(_WIN)
        self.setFixedWidth(250)

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        # Custom titlebar
        hdr = QWidget()
        hdr.setFixedHeight(24)
        hdr.setStyleSheet("background:#0a0606;border-bottom:1px solid #180e0e;")
        hdr_lo = QHBoxLayout(hdr)
        hdr_lo.setContentsMargins(8, 0, 6, 0)
        hdr_lo.addWidget(self._sec_lbl(t("win_settings").upper()))
        hdr_lo.addStretch()
        lo.addWidget(hdr)

        self._drag_pos = None
        hdr.mousePressEvent   = self._hp
        hdr.mouseMoveEvent    = self._hm
        hdr.mouseReleaseEvent = self._hr

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:#181212;}")
        inner = QWidget()
        inner.setStyleSheet("background:#181212;")
        inner_lo = QVBoxLayout(inner)
        inner_lo.setContentsMargins(10, 8, 10, 10)
        inner_lo.setSpacing(4)
        scroll.setWidget(inner)
        lo.addWidget(scroll)
        self._ilo = inner_lo

        # Language
        inner_lo.addWidget(self._sec_lbl(t("lang")))
        lang_row = QHBoxLayout(); lang_row.setSpacing(6)
        self._btn_en = QPushButton("EN")
        self._btn_ru = QPushButton("RU")
        for btn in (self._btn_en, self._btn_ru):
            btn.setFixedSize(50, 24)
        self._btn_en.clicked.connect(lambda: self._set_lang("EN"))
        self._btn_ru.clicked.connect(lambda: self._set_lang("RU"))
        lang_row.addWidget(self._btn_en)
        lang_row.addWidget(self._btn_ru)
        lang_row.addStretch()
        inner_lo.addLayout(lang_row)
        self._update_lang_btns()

        # Notifications
        inner_lo.addWidget(self._sec_lbl(t("notifications")))
        self._cb_sat = self._cb("notify_satanic", "Satanic")
        self._cb_ang = self._cb("notify_angelic", "Angelic")
        self._cb_her = self._cb("notify_heroic",  "Heroic")
        inner_lo.addWidget(self._cb_sat)
        inner_lo.addWidget(self._cb_ang)
        inner_lo.addWidget(self._cb_her)

        # Sound
        inner_lo.addWidget(self._sec_lbl(t("sound")))
        self._cb_snd = self._cb("sound_enabled", t("sound"))
        inner_lo.addWidget(self._cb_snd)

        # Save sessions
        inner_lo.addWidget(self._sec_lbl(t("save_sessions")))
        self._cb_save = self._cb("save_sessions", t("save_sessions"))
        inner_lo.addWidget(self._cb_save)

        # Session history
        inner_lo.addWidget(self._sec_lbl(t("history")))
        self._hist_lo = QVBoxLayout(); self._hist_lo.setSpacing(2)
        inner_lo.addLayout(self._hist_lo)
        inner_lo.addStretch()
        self._load_history()

        from PySide6.QtCore import QTimer
        QTimer(self, timeout=self._load_history, interval=15000).start()

    def _sec_lbl(self, text: str) -> QLabel:
        l = QLabel(text.upper())
        l.setStyleSheet(_SEC + "margin-top:6px;margin-bottom:2px;")
        return l

    def _cb(self, key: str, label: str) -> QCheckBox:
        cb = QCheckBox(label)
        cb.setStyleSheet(_CB)
        cb.setChecked(bool(config.get(key)))
        cb.stateChanged.connect(lambda v, k=key: config.set(k, bool(v)))
        return cb

    def _hp(self, e):
        from PySide6.QtCore import Qt as Q
        if e.button() == Q.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def _hm(self, e):
        from PySide6.QtCore import Qt as Q
        if self._drag_pos and e.buttons() & Q.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
    def _hr(self, e): self._drag_pos = None

    def _set_lang(self, lang: str):
        set_lang(lang); config.set("lang", lang)
        self._update_lang_btns()
        for cb in _lang_cbs:
            try: cb(lang)
            except Exception: pass

    def _update_lang_btns(self):
        cur = get_lang()
        self._btn_en.setStyleSheet(_ACTIVE if cur == "EN" else _BTN)
        self._btn_ru.setStyleSheet(_ACTIVE if cur == "RU" else _BTN)

    def on_lang_changed(self, cb): _lang_cbs.append(cb)

    def _load_history(self):
        while self._hist_lo.count():
            item = self._hist_lo.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        sessions = list_sessions()
        if not sessions:
            l = QLabel("—")
            l.setStyleSheet("color:#2a1a10;font-size:10px;font-family:'CookieRun Bold';background:transparent;")
            self._hist_lo.addWidget(l)
        else:
            for s in sessions[:5]:
                ts  = s.get("timestamp","")[:16].replace("T"," ")
                acc = s.get("character",{})
                gold = s.get("gold",{}).get("earned",0)
                dur  = s.get("session",{}).get("duration","")
                txt  = f"{ts}  {acc.get('name','?')} +{gold:,}g  {dur}"
                l = QLabel(txt)
                l.setWordWrap(True)
                l.setStyleSheet("color:#4a2a10;font-size:9px;font-family:'CookieRun Bold';background:transparent;")
                self._hist_lo.addWidget(l)

    def retranslate(self): pass
