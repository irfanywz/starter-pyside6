"""Dialog bergaya frameless (menggantikan QMessageBox). Gaya lewat QSS (#DialogFrame dst.).

    from app.ui.dialogs import confirm, info
    if confirm(self.window(), "Hapus?", "Data akan hilang.", ok_text="Hapus", danger=True): ...
    info(self.window(), "Selesai", "Proses berhasil.")
"""

from PySide6.QtCore import QEvent, QObject, QPoint, QPropertyAnimation, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Backdrop(QWidget):
    """Lapisan gelap semi-transparan di atas window utama saat dialog modal tampil (QSS #Backdrop)."""

    def __init__(self, target: QWidget) -> None:
        super().__init__(target)
        self._target = target
        self.setObjectName("Backdrop")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setGeometry(target.rect())
        target.installEventFilter(self)
        self._fx = QGraphicsOpacityEffect(self)
        self._fx.setOpacity(0.0)
        self.setGraphicsEffect(self._fx)
        self._anim = QPropertyAnimation(self._fx, b"opacity", self)
        self._anim.setDuration(160)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)

    @staticmethod
    def create(parent) -> "Backdrop | None":
        """Backdrop untuk window `parent` (memakai parent.backdrop_target() bila ada); None bila tak terlihat."""
        if parent is None or not parent.isVisible():
            return None
        getter = getattr(parent, "backdrop_target", None)
        target = getter() if callable(getter) else parent
        backdrop = Backdrop(target)
        backdrop.show()
        backdrop.raise_()
        backdrop._anim.start()
        return backdrop

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self._target and event.type() == QEvent.Resize:
            self.setGeometry(self._target.rect())
        return False

    def dismiss(self) -> None:
        self._target.removeEventFilter(self)
        self.hide()
        self.deleteLater()


class AppDialog(QDialog):
    def __init__(self, parent, title: str, message: str) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setMinimumWidth(400)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)  # ruang untuk shadow
        self.frame = QFrame()
        self.frame.setObjectName("DialogFrame")
        shadow = QGraphicsDropShadowEffect(self.frame)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.frame.setGraphicsEffect(shadow)
        outer.addWidget(self.frame)

        lay = QVBoxLayout(self.frame)
        lay.setContentsMargins(22, 20, 22, 18)
        lay.setSpacing(12)
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        msg = QLabel(message)
        msg.setObjectName("DialogMessage")
        msg.setWordWrap(True)
        lay.addWidget(title_label)
        lay.addWidget(msg)
        lay.addSpacing(6)
        self.buttons = QHBoxLayout()
        self.buttons.setSpacing(8)
        self.buttons.addStretch(1)
        lay.addLayout(self.buttons)

    def add_button(self, text: str, accept: bool, name: str = "", default: bool = False) -> QPushButton:
        btn = QPushButton(text)
        if name:
            btn.setObjectName(name)  # "Primary" | "Danger"
        btn.clicked.connect(self.accept if accept else self.reject)
        if default:
            btn.setDefault(True)
            btn.setFocus()
        self.buttons.addWidget(btn)
        return btn

    def run(self) -> bool:
        self.adjustSize()
        parent = self.parentWidget()
        if parent is not None and parent.isVisible():
            center = parent.frameGeometry().center()
        else:
            center = self.screen().availableGeometry().center()
        self.move(center - QPoint(self.width() // 2, self.height() // 2))
        backdrop = Backdrop.create(parent)
        try:
            return self.exec() == QDialog.Accepted
        finally:
            if backdrop is not None:
                backdrop.dismiss()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self.windowHandle() is not None:
            self.windowHandle().startSystemMove()
            return
        super().mousePressEvent(event)


def confirm(parent, title: str, message: str, ok_text: str = "OK",
            cancel_text: str = "Batal", danger: bool = False) -> bool:
    dlg = AppDialog(parent, title, message)
    dlg.add_button(cancel_text, accept=False)
    dlg.add_button(ok_text, accept=True, name="Danger" if danger else "Primary", default=True)
    return dlg.run()


def info(parent, title: str, message: str, ok_text: str = "OK") -> None:
    dlg = AppDialog(parent, title, message)
    dlg.add_button(ok_text, accept=True, name="Primary", default=True)
    dlg.run()
