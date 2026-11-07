from PySide6.QtCore import Property, QPropertyAnimation, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QAbstractButton


class ToggleSwitch(QAbstractButton):
    """Switch on/off beranimasi. Pakai sinyal `toggled(bool)` seperti checkbox.

    Warna dari palette (Highlight = on, Mid = off) sehingga mengikuti tema otomatis.
    """

    W, H, PAD = 40, 22, 3

    def __init__(self, checked: bool = False, parent=None) -> None:
        super().__init__(parent)
        self._offset = 1.0 if checked else 0.0
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.TabFocus)
        self.setFixedSize(self.W, self.H)
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(140)
        self.toggled.connect(self._animate)

    def sizeHint(self) -> QSize:
        return QSize(self.W, self.H)

    def _get_offset(self) -> float:
        return self._offset

    def _set_offset(self, value: float) -> None:
        self._offset = value
        self.update()

    offset = Property(float, _get_offset, _set_offset)

    def _animate(self, checked: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)
        pal = self.palette()
        off, on = pal.color(QPalette.Mid), pal.color(QPalette.Highlight)
        t = self._offset
        track = QColor(
            round(off.red() + (on.red() - off.red()) * t),
            round(off.green() + (on.green() - off.green()) * t),
            round(off.blue() + (on.blue() - off.blue()) * t),
        )
        p.setPen(Qt.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(QRectF(0, 0, self.W, self.H), self.H / 2, self.H / 2)
        d = self.H - 2 * self.PAD
        x = self.PAD + t * (self.W - d - 2 * self.PAD)
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(QRectF(x, self.PAD, d, d))
        if self.hasFocus():
            p.setBrush(Qt.NoBrush)
            p.setPen(QColor(on))
            p.drawRoundedRect(QRectF(0.5, 0.5, self.W - 1, self.H - 1), self.H / 2, self.H / 2)
