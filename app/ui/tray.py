"""Tray icon: klik = tampil/sembunyikan window, menu: Tampilkan/Sembunyikan + Keluar."""

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from ..meta import APP_DISPLAY_NAME
from ..paths import ICON_PNG


class AppTray(QSystemTrayIcon):
    def __init__(self, window) -> None:
        super().__init__(QIcon(str(ICON_PNG)), window)
        self._window = window
        self.setToolTip(APP_DISPLAY_NAME)

        self.menu = QMenu()
        self.toggle_action = QAction("Sembunyikan", self.menu)
        self.toggle_action.triggered.connect(self.toggle_window)
        quit_action = QAction("Keluar", self.menu)
        quit_action.triggered.connect(window.quit_app)
        self.menu.addAction(self.toggle_action)
        self.menu.addSeparator()
        self.menu.addAction(quit_action)
        self.menu.aboutToShow.connect(self._sync_label)
        self.setContextMenu(self.menu)

        self.activated.connect(self._on_activated)

    def _sync_label(self) -> None:
        visible = self._window.isVisible() and not self._window.isMinimized()
        self.toggle_action.setText("Sembunyikan" if visible else "Tampilkan")

    def _on_activated(self, reason) -> None:
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.toggle_window()

    def toggle_window(self) -> None:
        if self._window.isVisible() and not self._window.isMinimized():
            self._window.hide()
        else:
            self._window.show_window()
