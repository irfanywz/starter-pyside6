"""Jembatan ke main thread (Qt). Aman dipanggil dari thread mana pun.

`init()` dipanggil sekali di main.py (thread utama, setelah QApplication dibuat).
"""

import functools

from PySide6.QtCore import QObject, Signal


class _Bridge(QObject):
    _call = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._call.connect(self._run)

    def _run(self, fn) -> None:
        fn()


_bridge: _Bridge | None = None


def init() -> None:
    global _bridge
    _bridge = _Bridge()  # lahir di main thread -> slot selalu jalan di main thread


def call_in_main(fn, *args, **kwargs) -> None:
    if _bridge is None:
        raise RuntimeError("mainthread.init() belum dipanggil")
    _bridge._call.emit(functools.partial(fn, *args, **kwargs))
