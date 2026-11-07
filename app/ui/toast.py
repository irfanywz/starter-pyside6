"""Toast: notifikasi singkat di tengah bawah window. Pakai: ctx.toast("Teks", "success")."""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel

BOTTOM_GAP = 28  # jarak dari tepi bawah frame (px)


class Toast(QFrame):
    """Child dari frame utama. Satu toast pada satu waktu (yang baru menggantikan)."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 10)
        self.label = QLabel()
        self.label.setObjectName("ToastLabel")
        lay.addWidget(self.label)

        self._fx = QGraphicsOpacityEffect(self)
        self._fx.setOpacity(0.0)
        self.setGraphicsEffect(self._fx)
        self._anim = QPropertyAnimation(self._fx, b"opacity", self)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.finished.connect(self._on_anim_done)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)
        self.hide()

    def show_message(self, text: str, kind: str = "info", ms: int = 2500) -> None:
        """kind: "info" | "success" | "error"."""
        self._timer.stop()
        self._anim.stop()
        self.label.setText(text)
        self.setProperty("kind", kind)
        for w in (self, self.label):
            w.style().unpolish(w)
            w.style().polish(w)
        self.reposition()
        self.show()
        self.raise_()
        self._animate(1.0, 160)
        self._timer.start(ms)

    def reposition(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        self.setMaximumWidth(max(200, parent.width() - 48))
        self.adjustSize()
        self.move((parent.width() - self.width()) // 2, parent.height() - self.height() - BOTTOM_GAP)

    def _animate(self, end: float, duration: int) -> None:
        self._anim.stop()
        self._anim.setDuration(duration)
        self._anim.setStartValue(self._fx.opacity())
        self._anim.setEndValue(end)
        self._anim.start()

    def _fade_out(self) -> None:
        self._animate(0.0, 260)

    def _on_anim_done(self) -> None:
        if self._fx.opacity() <= 0.01:
            self.hide()
