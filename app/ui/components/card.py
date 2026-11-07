from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class Card(QFrame):
    """Kontainer berbingkai (QSS #Card) dengan judul opsional.

        card = Card("Umum"); card.add(SettingRow(...)); card.add_divider(); card.add(...)
    """

    def __init__(self, title: str = "") -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(18, 14, 18, 14)
        self.body.setSpacing(6)
        if title:
            label = QLabel(title)
            label.setObjectName("CardTitle")
            self.body.addWidget(label)

    def add(self, widget: QWidget) -> QWidget:
        self.body.addWidget(widget)
        return widget

    def add_divider(self) -> None:
        line = QFrame()
        line.setObjectName("Divider")
        line.setFixedHeight(1)
        self.body.addWidget(line)
