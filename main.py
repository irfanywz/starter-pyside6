"""Entry point. Dev: `uv run python main.py`."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app import errors, mainthread, startup
from app.logger import setup_logging
from app.meta import APP_DISPLAY_NAME, APP_VERSION
from app.paths import ICON_PNG, ensure_dirs
from app.settings import Settings
from app.single_instance import SingleInstance
from app.ui.main_window import AppContext, MainWindow
from app.ui.theme import apply_theme


def main() -> int:
    ensure_dirs()
    log = setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_DISPLAY_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setWindowIcon(QIcon(str(ICON_PNG)))
    app.setQuitOnLastWindowClosed(False)  # keluar diatur MainWindow (tray)
    mainthread.init()

    instance = SingleInstance()
    if not instance.try_acquire():
        log.info("Instance lain sudah berjalan; keluar")
        return 0
    log.info("Start %s v%s", APP_DISPLAY_NAME, APP_VERSION)

    settings = Settings()
    apply_theme(app, settings.get("theme"))

    ctx = AppContext(app, settings)
    win = MainWindow(ctx)
    instance.activated.connect(win.show_window)
    errors.install(lambda text: ctx.toast(text, "error", 4000))

    startup.sync()
    # Dijalankan oleh startup Windows (--minimized): langsung ke tray bila tersedia.
    if not (startup.MINIMIZED_FLAG in sys.argv and win.tray_ready()):
        win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
