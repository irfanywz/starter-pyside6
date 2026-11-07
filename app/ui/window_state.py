"""Simpan/pulihkan ukuran, posisi, dan status maximized window.

Posisi tersimpan yang tidak lagi terlihat (monitor dicabut/resolusi berubah) diabaikan -> window di tengah layar.
"""

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QGuiApplication


def _visible(rect: QRect) -> bool:
    """True bila bagian atas (area titlebar) window masih terlihat di salah satu layar."""
    head = QRect(rect.x(), rect.y(), rect.width(), 40)
    for screen in QGuiApplication.screens():
        inter = screen.availableGeometry().intersected(head)
        if inter.width() >= 100 and inter.height() >= 20:
            return True
    return False


def _center(win) -> None:
    area = QGuiApplication.primaryScreen().availableGeometry()
    win.move(area.center() - QPoint(win.width() // 2, win.height() // 2))


def restore(win, settings) -> None:
    area = QGuiApplication.primaryScreen().availableGeometry()
    w = min(int(settings.get("window_width")), area.width())
    h = min(int(settings.get("window_height")), area.height())
    win.resize(w, h)

    x, y = settings.get("window_x"), settings.get("window_y")
    if isinstance(x, int) and isinstance(y, int) and _visible(QRect(x, y, w, h)):
        win.move(x, y)
    else:
        _center(win)

    if settings.get("window_maximized"):
        win.setWindowState(win.windowState() | Qt.WindowMaximized)


def save(win, settings) -> None:
    maximized = win.isMaximized()
    geo = win.normalGeometry() if (maximized or win.isMinimized()) else win.geometry()
    settings.update(
        {
            "window_width": geo.width(),
            "window_height": geo.height(),
            "window_x": geo.x(),
            "window_y": geo.y(),
            "window_maximized": maximized,
        }
    )
