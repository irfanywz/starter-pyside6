"""Semua path aplikasi lewat sini. Jangan hardcode path di tempat lain.

Dev    : BASE_DIR = root proyek,   DATA_DIR = <root>/<APP_ID>_Data
Frozen : BASE_DIR = folder .exe,   DATA_DIR = <folder exe>/<APP_ID>_Data
"""

import os
import sys
from pathlib import Path

from .meta import DATA_DIR_NAME

FROZEN: bool = bool(getattr(sys, "frozen", False))

BASE_DIR: Path = (
    Path(sys.executable).resolve().parent
    if FROZEN
    else Path(__file__).resolve().parent.parent
)

# APP_DATA_DIR_OVERRIDE hanya untuk test (tools/smoke_test.py); jangan dipakai di produksi.
_override = os.environ.get("APP_DATA_DIR_OVERRIDE")
DATA_DIR: Path = Path(_override) if _override else BASE_DIR / DATA_DIR_NAME
LOG_DIR: Path = DATA_DIR / "logs"
SETTINGS_FILE: Path = DATA_DIR / "settings.json"
CUSTOM_QSS: Path = DATA_DIR / "custom.qss"  # override style oleh user, tanpa rebuild


def resource_path(relative: str) -> Path:
    """Path file bundel (assets, dll). Di frozen -> dalam folder <APP_ID>_System."""
    root = Path(getattr(sys, "_MEIPASS", BASE_DIR))
    return root / relative


ICON_PNG: Path = resource_path("assets/icon.png")
QSS_FILE: Path = resource_path("assets/styles/app.qss")


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
