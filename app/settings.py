"""Pengaturan aplikasi (JSON di DATA_DIR). Simpan otomatis, tanpa tombol Save."""

import json
import logging
from typing import Any

from .paths import SETTINGS_FILE

log = logging.getLogger("app.settings")

DEFAULTS: dict[str, Any] = {
    "theme": "dark",         # "dark" | "light"
    "close_to_tray": True,   # tombol close -> sembunyi ke tray, bukan keluar
    "window_width": 1000,
    "window_height": 680,
    "window_x": None,          # None = tengah layar
    "window_y": None,
    "window_maximized": False,
}


class Settings:
    def __init__(self) -> None:
        self._data: dict[str, Any] = dict(DEFAULTS)
        self._load()

    def _load(self) -> None:
        try:
            if SETTINGS_FILE.exists():
                self._data.update(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
        except Exception:
            log.exception("Gagal membaca settings, pakai default")

    def get(self, key: str) -> Any:
        return self._data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    def update(self, values: dict[str, Any]) -> None:
        """Set beberapa key sekaligus (satu kali tulis ke disk)."""
        self._data.update(values)
        self._save()

    def _save(self) -> None:
        tmp = SETTINGS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(SETTINGS_FILE)  # atomic
