"""Tema: token warna + template QSS (assets/styles/app.qss) + override user (Data/custom.qss).

Menambah warna baru: tambah key di kedua dict TOKENS, lalu pakai @key@ di QSS.
"""

import logging

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

from ..paths import CUSTOM_QSS, QSS_FILE

log = logging.getLogger("app.theme")

TOKENS: dict[str, dict[str, str]] = {
    "dark": {
        "bg": "#1e1f22",
        "surface": "#25262a",
        "surface_alt": "#2d2f33",
        "border": "#383a40",
        "hover": "#32343a",
        "text": "#e6e6e6",
        "text_muted": "#9a9da5",
        "accent": "#3d7eff",
        "accent_hover": "#5a93ff",
        "accent_soft": "rgba(61, 126, 255, 46)",
        "danger": "#e5484d",
        "success": "#2fb344",
        "backdrop": "rgba(0, 0, 0, 150)",
    },
    "light": {
        "bg": "#f6f7f9",
        "surface": "#ffffff",
        "surface_alt": "#eceef2",
        "border": "#d8dbe2",
        "hover": "#e6e9ef",
        "text": "#22252b",
        "text_muted": "#6b7078",
        "accent": "#3d7eff",
        "accent_hover": "#2f6be6",
        "accent_soft": "rgba(61, 126, 255, 36)",
        "danger": "#e5484d",
        "success": "#2fb344",
        "backdrop": "rgba(0, 0, 0, 90)",
    },
}


# Satu keluarga font & skala ukuran untuk SELURUH UI (titlebar, navigasi, halaman, menu, tray).
# Ubah di sini agar seragam; QSS memakai @font_family@, @fs_small@, @fs_base@, @fs_heading@, @fs_title@.
FONT_FAMILIES = ["Segoe UI", "Inter", "Helvetica Neue", "Arial"]
FONT = {
    "font_family": ", ".join(f'"{f}"' for f in FONT_FAMILIES) + ", sans-serif",
    "fs_small": "12px",
    "fs_base": "13px",
    "fs_heading": "16px",
    "fs_title": "22px",
}


def tokens(name: str) -> dict[str, str]:
    return TOKENS.get(name, TOKENS["dark"])


def icon_color(name: str) -> str:
    return tokens(name)["text"]


def _read(path) -> str:
    try:
        return path.read_text(encoding="utf-8") if path.exists() else ""
    except Exception:
        log.exception("Gagal membaca %s", path)
        return ""


def _render(template: str, tk: dict[str, str]) -> str:
    for key, value in tk.items():
        template = template.replace(f"@{key}@", value)
    return template


def _palette(tk: dict[str, str]) -> QPalette:
    pal = QPalette()
    mapping = {
        QPalette.Window: tk["bg"],
        QPalette.WindowText: tk["text"],
        QPalette.Base: tk["surface"],
        QPalette.AlternateBase: tk["surface_alt"],
        QPalette.Text: tk["text"],
        QPalette.Button: tk["surface_alt"],
        QPalette.ButtonText: tk["text"],
        QPalette.ToolTipBase: tk["surface_alt"],
        QPalette.ToolTipText: tk["text"],
        QPalette.Mid: tk["border"],
        QPalette.Highlight: tk["accent"],
        QPalette.HighlightedText: "#ffffff",
    }
    for role, color in mapping.items():
        pal.setColor(role, QColor(color))
    return pal


def _app_font() -> QFont:
    font = QFont()
    font.setFamilies(FONT_FAMILIES)
    font.setPixelSize(int(FONT["fs_base"].removesuffix("px")))
    return font


def apply_theme(app: QApplication, name: str) -> None:
    tk = {**tokens(name), **FONT}
    app.setStyle("Fusion")
    app.setFont(_app_font())
    app.setPalette(_palette(tk))
    qss = _render(_read(QSS_FILE) + "\n" + _read(CUSTOM_QSS), tk)
    app.setStyleSheet(qss)
