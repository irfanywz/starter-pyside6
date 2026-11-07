import qtawesome as qta
from PySide6.QtCore import QEvent, QObject, QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from ..meta import APP_DISPLAY_NAME, APP_VERSION
from ..paths import ICON_PNG
from .frameless import FramelessRoot
from .pages import PAGES
from .theme import icon_color, tokens
from .titlebar import TitleBar
from . import window_state
from .toast import Toast
from .tray import AppTray


class AppContext(QObject):
    """Objek bersama yang dioper ke semua halaman (settings, app, sinyal global)."""

    theme_changed = Signal(str)

    def __init__(self, app, settings) -> None:
        super().__init__()
        self.app = app
        self.settings = settings
        self.quitting = False  # True = close benar-benar keluar (bukan ke tray)

    def toast(self, text: str, kind: str = "info", ms: int = 2500) -> None:
        """Tampilkan toast. Diganti implementasinya oleh MainWindow."""


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self.ctx = ctx
        self._tray_hint_shown = False

        self.setWindowTitle(f"{APP_DISPLAY_NAME} v{APP_VERSION}")
        self.setWindowIcon(QIcon(str(ICON_PNG)))
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumSize(640, 420)
        window_state.restore(self, ctx.settings)

        # root (zona resize) -> frame (border/rounded) -> titlebar + body
        self.root = FramelessRoot(self)
        self.setCentralWidget(self.root)

        self.frame = QFrame()
        self.frame.setObjectName("AppFrame")
        self.frame.setProperty("maximized", False)
        self.root.layout().addWidget(self.frame)
        outer = QVBoxLayout(self.frame)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.titlebar = TitleBar(self, f"{APP_DISPLAY_NAME}")
        outer.addWidget(self.titlebar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        outer.addLayout(body, 1)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setAttribute(Qt.WA_StyledBackground, True)
        self.sidebar.setFixedWidth(190)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(0, 8, 0, 8)
        side.setSpacing(2)
        self.stack = QStackedWidget()
        self.stack.setObjectName("Pages")
        body.addWidget(self.sidebar)
        body.addWidget(self.stack, 1)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self._buttons: list[tuple[QPushButton, str]] = []
        top_btns: list[QPushButton] = []
        bottom_btns: list[QPushButton] = []
        for i, spec in enumerate(PAGES):
            btn = QPushButton("  " + spec.title)  # spasi = jarak ikon-teks
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setIconSize(QSize(18, 18))
            self.group.addButton(btn, i)
            self._buttons.append((btn, spec.icon))
            self.stack.addWidget(spec.factory(ctx))
            (bottom_btns if spec.bottom else top_btns).append(btn)
        for btn in top_btns:
            side.addWidget(btn)
        side.addStretch(1)
        if bottom_btns:
            side.addWidget(self._nav_divider())
            for btn in bottom_btns:
                side.addWidget(btn)

        self.group.idClicked.connect(self._go)
        ctx.theme_changed.connect(self._refresh_icons)
        self._refresh_icons(ctx.settings.get("theme"))
        self._buttons[0][0].setChecked(True)
        self._go(0)

        self.toaster = Toast(self.frame)
        ctx.toast = self.toaster.show_message

        self.tray = AppTray(self)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    # ---------- navigasi ----------
    @staticmethod
    def _nav_divider() -> QWidget:
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 6, 14, 6)
        line = QFrame()
        line.setObjectName("NavDivider")
        line.setFixedHeight(1)
        lay.addWidget(line)
        return box

    def _go(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        if hasattr(page, "on_show"):
            page.on_show()

    def _refresh_icons(self, theme_name: str) -> None:
        color = icon_color(theme_name)
        accent = tokens(theme_name)["accent"]
        for btn, icon in self._buttons:
            # color_on* = warna ikon saat tombol aktif (checked)
            btn.setIcon(qta.icon(icon, color=color, color_on=accent, color_on_active=accent))
        self.titlebar.refresh_icons(theme_name)

    # ---------- state window ----------
    def changeEvent(self, event) -> None:
        if event.type() == QEvent.WindowStateChange:
            maximized = self.isMaximized()
            self.frame.setProperty("maximized", maximized)
            self.frame.style().unpolish(self.frame)
            self.frame.style().polish(self.frame)
            self.root.sync_margin()
            self.titlebar.refresh_icons(self.ctx.settings.get("theme"))
        super().changeEvent(event)

    def backdrop_target(self):
        """Widget yang ditutup backdrop saat dialog modal tampil."""
        return self.frame

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "toaster"):
            self.toaster.reposition()

    def show_window(self) -> None:
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.show()
        self.raise_()
        self.activateWindow()

    # ---------- close / tray ----------
    def tray_ready(self) -> bool:
        return QSystemTrayIcon.isSystemTrayAvailable() and self.tray.isVisible()

    def closeEvent(self, event) -> None:
        if (
            not self.ctx.quitting
            and self.ctx.settings.get("close_to_tray")
            and self.tray_ready()
        ):
            event.ignore()
            window_state.save(self, self.ctx.settings)
            self.hide()
            if not self._tray_hint_shown:
                self._tray_hint_shown = True
                self.tray.showMessage(
                    APP_DISPLAY_NAME,
                    "Aplikasi masih berjalan di tray. Klik ikon tray untuk membuka.",
                    QSystemTrayIcon.Information,
                    3000,
                )
            return
        window_state.save(self, self.ctx.settings)
        self.tray.hide()
        event.accept()
        self.ctx.app.quit()

    def quit_app(self) -> None:
        """Keluar sungguhan (menu tray -> Keluar)."""
        self.ctx.quitting = True
        self.close()
