from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SettingRow(QWidget):
    """Satu baris pengaturan: judul + deskripsi di kiri, kontrol (mis. ToggleSwitch) di kanan."""

    def __init__(self, title: str, description: str = "", control: QWidget | None = None) -> None:
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 6, 0, 6)
        row.setSpacing(16)
        text = QVBoxLayout()
        text.setSpacing(1)
        t = QLabel(title)
        t.setObjectName("SettingTitle")
        text.addWidget(t)
        if description:
            d = QLabel(description)
            d.setObjectName("SettingDesc")
            d.setWordWrap(True)
            text.addWidget(d)
        row.addLayout(text, 1)
        if control is not None:
            row.addWidget(control, 0, Qt.AlignVCenter)
