import platform

from PySide6 import __version__ as PYSIDE_VERSION
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ...meta import APP_DISPLAY_NAME, APP_VERSION
from ...paths import DATA_DIR, FROZEN, LOG_DIR
from ..components import Card, PageHeader
from .base_page import BasePage


class AboutPage(BasePage):
    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)
        lay.setAlignment(Qt.AlignTop)

        lay.addWidget(PageHeader("Tentang", f"{APP_DISPLAY_NAME} v{APP_VERSION}"))

        self.info_text = (
            f"{APP_DISPLAY_NAME} v{APP_VERSION}\n"
            f"Python {platform.python_version()} · PySide6 {PYSIDE_VERSION}\n"
            f"{platform.platform()}\n"
            f"Mode: {'exe (frozen)' if FROZEN else 'dev'}\n"
            f"Data: {DATA_DIR}"
        )
        card = Card("Info")
        label = QLabel(self.info_text)
        label.setObjectName("Muted")
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        card.add(label)
        lay.addWidget(card)

        row = QHBoxLayout()
        row.setSpacing(8)
        for text, slot in (
            ("Buka folder data", self._open_data),
            ("Buka log", self._open_log),
            ("Salin info", self._copy_info),
        ):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch(1)
        lay.addLayout(row)

    def _open_data(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(DATA_DIR)))

    def _open_log(self) -> None:
        log_file = LOG_DIR / "app.log"
        if log_file.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_file)))
        else:
            self.ctx.toast("File log belum ada", "error")

    def _copy_info(self) -> None:
        QApplication.clipboard().setText(self.info_text)
        self.ctx.toast("Info disalin ke clipboard", "success")
