from PySide6.QtWidgets import QWidget


class BasePage(QWidget):
    """Kelas dasar semua halaman. Override on_show() bila perlu refresh data."""

    def on_show(self) -> None:
        pass
