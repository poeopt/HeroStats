from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal
from src.utils import config


class CollapsibleSection(QWidget):
    toggled = Signal()

    def __init__(self, title: str, cfg_key: str, default_open: bool = True):
        QWidget.__init__(self)
        self._key  = f"section_{cfg_key}"
        self._open = config.get(self._key)
        if self._open is None:
            self._open = default_open

        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        self._btn = QPushButton()
        self._btn.setObjectName("CollapseBtn")  # стиль из QSS темы
        self._btn.setFixedHeight(15)
        self._btn.clicked.connect(self._toggle)
        lo.addWidget(self._btn)

        self._body = QWidget()
        self._body.setObjectName("CollapseBody")  # стиль из QSS темы
        self._body_lo = QVBoxLayout(self._body)
        self._body_lo.setContentsMargins(0, 0, 0, 0)
        self._body_lo.setSpacing(2)
        lo.addWidget(self._body)

        self._title = title
        self._set_btn_text()
        self._body.setVisible(self._open)

    def add_widget(self, w: QWidget) -> None:
        self._body_lo.addWidget(w)

    def is_open(self) -> bool:
        return self._open

    def _toggle(self) -> None:
        self._open = not self._open
        self._body.setVisible(self._open)
        self._set_btn_text()
        config.set(self._key, self._open)
        self.toggled.emit()

    def _set_btn_text(self) -> None:
        arrow = "▼" if self._open else "▶"
        self._btn.setText(f"  {arrow}  {self._title.upper()}")
