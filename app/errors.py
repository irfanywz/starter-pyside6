"""Penangkap exception global: dicatat ke log + toast error. Pasang sekali di main.py."""

import logging
import sys
import threading

from .mainthread import call_in_main

log = logging.getLogger("app.errors")
_show = None  # callable(text) -> menampilkan toast error


def _message(exc: BaseException) -> str:
    text = str(exc) or exc.__class__.__name__
    if len(text) > 120:
        text = text[:117] + "..."
    return f"Terjadi kesalahan: {text}"


def notify(exc: BaseException) -> None:
    """Tampilkan toast error (aman dari thread mana pun). Tidak mencatat log."""
    if _show is not None:
        call_in_main(_show, _message(exc))


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    log.error("Exception tidak tertangani", exc_info=(exc_type, exc_value, exc_tb))
    notify(exc_value)


def _thread_hook(args) -> None:
    _excepthook(args.exc_type, args.exc_value, args.exc_traceback)


def install(show) -> None:
    global _show
    _show = show
    sys.excepthook = _excepthook
    threading.excepthook = _thread_hook
