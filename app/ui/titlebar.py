"""Custom titlebar: ikon, judul, tombol minimize / maximize-restore / close.

Tampilan diatur lewat QSS (#TitleBar, #TitleLabel, #TitleBtn, #CloseBtn).
"""

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QToolButton, QWidget

from ..paths import ICON_PNG
from .theme import icon_color


class TitleBar(QWidget):
    def __init__(self, window, title: str) -> None:
        super().__init__()
        self._window = window
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(36)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 0, 0)
        lay.setSpacing(8)

        icon = QLabel()
        icon.setPixmap(QIcon(str(ICON_PNG)).pixmap(18, 18))
        self.title = QLabel(title)
        self.title.setObjectName("TitleLabel")
        lay.addWidget(icon)
        lay.addWidget(self.title)
        lay.addStretch(1)

        self.btn_min = self._button("TitleBtn", self._window.showMinimized)
        self.btn_max = self._button("TitleBtn", self._toggle_max)
        self.btn_close = self._button("CloseBtn", self._window.close)
        for b in (self.btn_min, self.btn_max, self.btn_close):
            lay.addWidget(b)

    def _button(self, name: str, slot) -> QToolButton:
        b = QToolButton()
        b.setObjectName(name)
        b.setFocusPolicy(Qt.NoFocus)
        b.clicked.connect(slot)
        return b

    def _toggle_max(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def refresh_icons(self, theme_name: str) -> None:
        color = icon_color(theme_name)
        maximized = self._window.isMaximized()
        self.btn_min.setIcon(qta.icon("fa5s.minus", color=color))
        self.btn_max.setIcon(qta.icon("fa5.clone" if maximized else "fa5.square", color=color))
        self.btn_close.setIcon(qta.icon("fa5s.times", color=color))

    # Drag window & double-click maximize
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            handle = self._window.windowHandle()
            if handle is not None:
                handle.startSystemMove()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._toggle_max()
        super().mouseDoubleClickEvent(event)
