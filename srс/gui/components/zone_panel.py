from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from src.consts.satanic_buffs import get_buff_description
from src.consts.i18n import get_lang


class _BuffRow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        lo = QHBoxLayout(self)
        lo.setContentsMargins(8, 1, 8, 1)
        lo.setSpacing(6)
        self._icon = QLabel()
        self._icon.setFixedSize(16, 16)
        self._name = QLabel()
        self._name.setObjectName("BName")
        self._name.setFixedWidth(130)
        self._desc = QLabel()
        self._desc.setObjectName("BDesc")
        self._desc.setWordWrap(True)
        lo.addWidget(self._icon)
        lo.addWidget(self._name)
        lo.addWidget(self._desc, 1)
        self.hide()

    def set(self, buff, lang: str) -> None:
        img = QImage(buff.buff_icon)
        if not img.isNull():
            self._icon.setPixmap(QPixmap.fromImage(img).scaled(
                16, 16,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        self._name.setText(buff.buff_name)
        desc = get_buff_description(buff.buff_name, lang)
        if not desc and hasattr(buff, 'get_description'):
            desc = buff.get_description(lang)
        self._desc.setText(desc or "")
        self.show()


class ZonePanel(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.setObjectName("ZonePanel")  # стиль из QSS темы
        self._info = None

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 4, 0, 4)
        lo.setSpacing(2)

        nr = QHBoxLayout()
        nr.setContentsMargins(8, 0, 8, 2)
        self._prefix = QLabel("◆")
        self._prefix.setObjectName("NoZone")  # переиспользуем dim цвет
        self._zname = QLabel("—")
        self._zname.setObjectName("ZName")
        nr.addWidget(self._prefix)
        nr.addWidget(self._zname)
        nr.addStretch()
        lo.addLayout(nr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("max-height:1px; border:none; margin:0 6px;")
        lo.addWidget(sep)

        self._rows = [_BuffRow() for _ in range(3)]
        for r in self._rows:
            lo.addWidget(r)

        self._ph = QLabel("  Войдите в Satanic Zone")
        self._ph.setObjectName("NoZone")
        lo.addWidget(self._ph)

    def update_zone(self, sz_info) -> None:
        self._info = sz_info
        lang = get_lang()
        if sz_info is None:
            self._zname.setText("—")
            for r in self._rows: r.hide()
            self._ph.show()
            return
        self._ph.hide()
        self._zname.setText(sz_info.satanic_zone)
        for i, row in enumerate(self._rows):
            if i < len(sz_info.buffs):
                row.set(sz_info.buffs[i], lang)
            else:
                row.hide()

    def retranslate(self) -> None:
        if self._info is not None:
            self.update_zone(self._info)
