"""Jalankan saat startup (Windows, HKCU Run). Hanya aktif pada build exe (frozen).

Sumber kebenaran = registry, bukan settings.json. Entri menjalankan exe dengan
`--minimized` sehingga aplikasi langsung bersembunyi di tray.
"""

import logging
import sys

from .meta import APP_ID
from .paths import FROZEN

log = logging.getLogger("app.startup")

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
MINIMIZED_FLAG = "--minimized"


def is_supported() -> bool:
    return sys.platform == "win32" and FROZEN


def _command() -> str:
    return f'"{sys.executable}" {MINIMIZED_FLAG}'


def _read() -> str | None:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            return winreg.QueryValueEx(key, APP_ID)[0]
    except OSError:
        return None


def is_enabled() -> bool:
    return is_supported() and _read() is not None


def set_enabled(enabled: bool) -> bool:
    """Return True bila berhasil."""
    if not is_supported():
        return False
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                winreg.SetValueEx(key, APP_ID, 0, winreg.REG_SZ, _command())
            else:
                try:
                    winreg.DeleteValue(key, APP_ID)
                except FileNotFoundError:
                    pass
        return True
    except OSError:
        log.exception("Gagal mengubah startup")
        return False


def sync() -> None:
    """Jika aktif tapi path exe berubah (folder dipindah), perbarui entri."""
    if is_enabled() and _read() != _command():
        set_enabled(True)
