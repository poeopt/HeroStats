from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt
from src.consts.i18n import get_lang

_ITEMS_EN = [
    ("⏱ Session Timer",      "Time since start or last Reset."),
    ("🪙 Gold",               "Current / earned this session / per hour."),
    ("⭐ Experience",         "Total / earned / per hour."),
    ("📦 Drops",              "Angelic·Heroic·Satanic counts. (MF) = Magic Find drops."),
    ("🔮 Satanic Zone",       "Current zone + 3 buffs with descriptions (RU/EN).\nUpdates when you enter a Satanic Zone."),
    ("🗼 Chaos Tower",        "Floors cleared total / this session / boss kills. Collapsible."),
    ("🌀 Wormhole",           "Best level per act A1–A8. Separate from Chaos Tower."),
    ("📋 Drop Log",           "Last 50 drops: time·rarity·tier·quality·sockets·MF.\nCustom title bar — drag to move."),
    ("📊 Zone Efficiency",    "Gold/h, XP/h, Sat/h per zone. % = vs best zone.\nNotes field for strategy. Sort by ⭐/G/XP/Sat/Time."),
    ("⚙ Settings",           "Language RU/EN · Notifications · Sound · Save sessions."),
    ("⎘ Copy",                "Copies full stats to clipboard (for Discord)."),
    ("↻ Reset",              "Resets session counters. Character data is kept."),
    ("🔔 Notifications",      "Toast + sound on Satanic/Angelic/Heroic/Mail drops.\nCustom WAV: assets/sounds/custom_satanic.wav (max 5s)"),
    ("☠ Deaths",             "Shown next to timer when deaths > 0."),
    ("Discord",               "discord.gg/SjkJM6nv"),
]
_ITEMS_RU = [
    ("⏱ Таймер сессии",      "Время с запуска или сброса."),
    ("🪙 Золото",             "Текущее / заработано / в час."),
    ("⭐ Опыт",               "Всего / за сессию / в час."),
    ("📦 Дропы",              "Ангел·Героич·Сатаник. (MF) = с магическим поиском."),
    ("🔮 Сатаническая зона",  "Текущая зона + 3 баффа с описанием (RU/EN).\nОбновляется при входе в Satanic Zone."),
    ("🗼 Башня Хаоса",        "Этажей всего / за сессию / боссов. Сворачивается."),
    ("🌀 Вормхол",            "Лучший уровень по актам A1–A8. Отдельно от Башни."),
    ("📋 Лог дропов",         "Последние 50 предметов: время·редкость·тир·качество·сокеты·MF.\nПеретаскивается за заголовок."),
    ("📊 Эффективность зон",  "Золото/ч, Опыт/ч, Сат/ч по каждой зоне. % = от лучшей.\nЗаметки о стратегии. Сортировка: ⭐/G/XP/Сат/Время."),
    ("⚙ Настройки",          "Язык RU/EN · Уведомления · Звук · Сохранение сессий."),
    ("⎘ Копировать",         "Копирует всю статистику в буфер (для Discord)."),
    ("↻ Сброс",              "Сбрасывает счётчики. Данные персонажа сохраняются."),
    ("🔔 Уведомления",        "Toast + звук при Сатаник/Ангел/Героич/Почте.\nКастомный WAV: assets/sounds/custom_satanic.wav (макс 5с)"),
    ("☠ Смерти",             "Показываются рядом с таймером когда > 0."),
    ("Discord",               "discord.gg/SjkJM6nv"),
]


class FaqWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self, None,
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("QWidget{background:#181212;}")
        self.setFixedWidth(330)

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        hdr = QWidget()
        hdr.setFixedHeight(24)
        hdr.setStyleSheet("background:#0a0606;border-bottom:1px solid #180e0e;")
        hdr_lo = QHBoxLayout(hdr)
        hdr_lo.setContentsMargins(8, 0, 6, 0)
        self._title_lbl = QLabel("? СПРАВКА / FAQ")
        self._title_lbl.setStyleSheet(
            "color:#5a3020;font-size:9px;letter-spacing:1px;"
            "font-family:'CookieRun Bold';background:transparent;border:none;")
        hdr_lo.addWidget(self._title_lbl)
        lo.addWidget(hdr)

        self._drag_pos = None
        hdr.mousePressEvent   = self._hp
        hdr.mouseMoveEvent    = self._hm
        hdr.mouseReleaseEvent = self._hr

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:#181212;}")
        self._inner = QWidget()
        self._inner.setStyleSheet("background:#181212;")
        self._ilo = QVBoxLayout(self._inner)
        self._ilo.setContentsMargins(10, 8, 10, 10)
        self._ilo.setSpacing(4)
        scroll.setWidget(self._inner)
        lo.addWidget(scroll)

        self._build()

    def _hp(self, e):
        from PySide6.QtCore import Qt as Q
        if e.button() == Q.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def _hm(self, e):
        from PySide6.QtCore import Qt as Q
        if self._drag_pos and e.buttons() & Q.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
    def _hr(self, e): self._drag_pos = None

    def _build(self):
        while self._ilo.count():
            item = self._ilo.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        items = _ITEMS_RU if get_lang() == "RU" else _ITEMS_EN
        for title, desc in items:
            tl = QLabel(title)
            tl.setStyleSheet(
                "color:#CA1717;font-size:11px;font-family:'CookieRun Bold';"
                "border-bottom:1px solid #1a0808;padding-bottom:1px;margin-top:4px;"
                "background:transparent;")
            dl = QLabel(desc)
            dl.setWordWrap(True)
            dl.setStyleSheet("color:#5a3020;font-size:10px;font-family:'CookieRun Bold';background:transparent;border:none;")
            self._ilo.addWidget(tl)
            self._ilo.addWidget(dl)
        self._ilo.addStretch()
        self.setFixedHeight(min(len(items)*48 + 50, 500))

    def retranslate(self): self._build()
