"""Window frameless: root widget dengan margin transparan sebagai zona resize.

Resize & move memakai API native Qt (startSystemResize / startSystemMove)
sehingga perilaku (snap, dsb.) mengikuti OS.
"""

import operator
from functools import reduce

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QVBoxLayout, QWidget

MARGIN = 6  # lebar zona resize (px)


class FramelessRoot(QWidget):
    """Central widget. Isi UI ditaruh di `self.layout()` (margin = zona resize)."""

    def __init__(self, window) -> None:
        super().__init__(window)
        self.setObjectName("Root")
        self.setMouseTracking(True)
        self._window = window
        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        self.sync_margin()

    def paintEvent(self, _event) -> None:
        # Piksel nyaris transparan (alpha 1/255) agar margin resize tetap menerima klik di Windows.
        # JANGAN lewat QSS rgba(0,0,0,1): Qt membaca alpha 1 sebagai opak -> muncul border hitam.
        QPainter(self).fillRect(self.rect(), QColor(0, 0, 0, 1))

    def _resizable(self) -> bool:
        return not (self._window.isMaximized() or self._window.isFullScreen())

    def sync_margin(self) -> None:
        m = MARGIN if self._resizable() else 0
        self.layout().setContentsMargins(m, m, m, m)

    def _edges(self, pos):
        if not self._resizable():
            return None
        r = self.rect()
        found = []
        if pos.x() <= MARGIN:
            found.append(Qt.LeftEdge)
        if pos.x() >= r.width() - MARGIN:
            found.append(Qt.RightEdge)
        if pos.y() <= MARGIN:
            found.append(Qt.TopEdge)
        if pos.y() >= r.height() - MARGIN:
            found.append(Qt.BottomEdge)
        return reduce(operator.or_, found) if found else None

    @staticmethod
    def _cursor_for(edges) -> Qt.CursorShape:
        left, right = bool(edges & Qt.LeftEdge), bool(edges & Qt.RightEdge)
        top, bottom = bool(edges & Qt.TopEdge), bool(edges & Qt.BottomEdge)
        if (left and top) or (right and bottom):
            return Qt.SizeFDiagCursor
        if (right and top) or (left and bottom):
            return Qt.SizeBDiagCursor
        if left or right:
            return Qt.SizeHorCursor
        return Qt.SizeVerCursor

    def mouseMoveEvent(self, event) -> None:
        edges = self._edges(event.position().toPoint())
        if edges is None:
            self.unsetCursor()
        else:
            self.setCursor(self._cursor_for(edges))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            edges = self._edges(event.position().toPoint())
            handle = self._window.windowHandle()
            if edges is not None and handle is not None:
                handle.startSystemResize(edges)
                return
        super().mousePressEvent(event)

    def leaveEvent(self, event) -> None:
        self.unsetCursor()
        super().leaveEvent(event)
