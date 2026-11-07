import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ...meta import APP_DISPLAY_NAME, APP_VERSION
from ...paths import DATA_DIR
from ...workers import run_async
from ..dialogs import confirm
from .base_page import BasePage


def _slow_task(progress):
    """Contoh pekerjaan berat di background thread."""
    for step in range(1, 4):
        time.sleep(0.6)
        progress(step)
    return "3 langkah"


class HomePage(BasePage):
    """Beranda + panel demo fitur starter. Hapus/ganti panel demo di aplikasi nyata."""

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(10)

        title = QLabel(APP_DISPLAY_NAME)
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignCenter)
        info = QLabel(f"v{APP_VERSION}\nData: {DATA_DIR}")
        info.setObjectName("Muted")
        info.setAlignment(Qt.AlignCenter)
        info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(title)
        lay.addWidget(info)
        lay.addSpacing(12)

        toast_row = self._row()
        for label, kind, text in (
            ("Toast Info", "info", "Ini toast info"),
            ("Toast Sukses", "success", "Berhasil disimpan"),
            ("Toast Error", "error", "Terjadi kesalahan"),
        ):
            btn = QPushButton(label)
            btn.clicked.connect(lambda _=False, t=text, k=kind: ctx.toast(t, k))
            toast_row.addWidget(btn)
        lay.addLayout(toast_row)

        demo_row = self._row()
        for label, slot in (
            ("Uji Worker", self._test_worker),
            ("Uji Dialog", self._test_dialog),
            ("Uji Error", self._test_error),
        ):
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            demo_row.addWidget(btn)
        lay.addLayout(demo_row)

    @staticmethod
    def _row() -> QHBoxLayout:
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.setSpacing(8)
        return row

    def _test_worker(self) -> None:
        self.ctx.toast("Worker berjalan di background...", "info", 1200)
        run_async(
            _slow_task,
            on_progress=lambda v: self.ctx.toast(f"Langkah {v}/3", "info", 700),
            on_result=lambda r: self.ctx.toast(f"Worker selesai: {r}", "success"),
        )

    def _test_dialog(self) -> None:
        ok = confirm(
            self.window(), "Hapus data?", "Ini contoh dialog konfirmasi bergaya frameless.",
            ok_text="Hapus", danger=True,
        )
        self.ctx.toast("Dikonfirmasi" if ok else "Dibatalkan", "success" if ok else "info")

    def _test_error(self) -> None:
        raise RuntimeError("Contoh error tidak tertangani")  # ditangkap errors.py -> log + toast
