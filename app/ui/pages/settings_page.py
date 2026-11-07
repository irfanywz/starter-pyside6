from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from ... import startup
from ..components import Card, PageHeader, SettingRow, ToggleSwitch
from ..theme import apply_theme
from .base_page import BasePage


class SettingsPage(BasePage):
    """Pengaturan otomatis tersimpan saat diubah (tanpa tombol Simpan)."""

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self._reverting = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(PageHeader("Pengaturan", "Perubahan tersimpan otomatis"))

        card = Card("Umum")
        self.dark = ToggleSwitch(ctx.settings.get("theme") == "dark")
        self.dark.toggled.connect(self._on_dark)
        card.add(SettingRow("Mode gelap", "Ganti tema terang / gelap", self.dark))
        card.add_divider()

        self.tray = ToggleSwitch(bool(ctx.settings.get("close_to_tray")))
        self.tray.toggled.connect(lambda v: ctx.settings.set("close_to_tray", v))
        card.add(SettingRow("Tutup ke tray", "Tombol close menyembunyikan aplikasi ke tray", self.tray))
        card.add_divider()

        self.startup = ToggleSwitch(startup.is_enabled())
        if startup.is_supported():
            self.startup.toggled.connect(self._on_startup)
        else:
            self.startup.setEnabled(False)
            self.startup.setToolTip("Hanya tersedia pada versi exe di Windows")
        card.add(
            SettingRow("Jalankan saat Windows startup", "Langsung ke tray saat Windows menyala", self.startup)
        )
        lay.addWidget(card)

    def _on_dark(self, checked: bool) -> None:
        name = "dark" if checked else "light"
        self.ctx.settings.set("theme", name)
        apply_theme(self.ctx.app, name)
        self.ctx.theme_changed.emit(name)

    def _on_startup(self, checked: bool) -> None:
        if self._reverting:
            return
        if not startup.set_enabled(checked):
            self._reverting = True
            self.startup.setChecked(not checked)
            self._reverting = False
            self.ctx.toast("Gagal mengubah pengaturan startup", "error")
            return
        self.ctx.toast(
            "Akan berjalan saat Windows menyala" if checked else "Tidak lagi berjalan saat startup",
            "success",
        )
