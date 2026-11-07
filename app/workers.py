"""Helper background task (QThreadPool) supaya UI tidak freeze.

    from app.workers import run_async

    def heavy(progress):               # parameter `progress` opsional
        for i in range(10):
            ...; progress(i + 1)
        return "selesai"

    run_async(heavy, on_result=lambda r: ctx.toast(r, "success"),
              on_progress=lambda v: ..., on_error=lambda e: ...)

- Semua callback (on_result/on_error/on_progress/on_finished) berjalan di MAIN thread.
- Tanpa on_error: error dicatat ke log + toast error otomatis.
- Panggil run_async dari main thread. Jangan sentuh widget di dalam fungsi worker.
"""

import inspect
import logging
from typing import Any, Callable

from PySide6.QtCore import QRunnable, QThreadPool

from . import errors
from .mainthread import call_in_main

log = logging.getLogger("app.workers")


class Worker(QRunnable):
    def __init__(self, fn, args, kwargs, on_result, on_error, on_progress, on_finished) -> None:
        super().__init__()
        self.setAutoDelete(True)
        self._fn, self._args, self._kwargs = fn, args, kwargs
        self._on_result, self._on_error = on_result, on_error
        self._on_progress, self._on_finished = on_progress, on_finished
        try:
            self._wants_progress = "progress" in inspect.signature(fn).parameters
        except (TypeError, ValueError):
            self._wants_progress = False

    def run(self) -> None:
        kwargs = dict(self._kwargs)
        if self._wants_progress:
            cb = self._on_progress
            kwargs["progress"] = (lambda v: call_in_main(cb, v)) if cb else (lambda v: None)
        try:
            result = self._fn(*self._args, **kwargs)
        except Exception as exc:
            log.exception("Worker gagal: %s", getattr(self._fn, "__name__", self._fn))
            if self._on_error:
                call_in_main(self._on_error, exc)
            else:
                errors.notify(exc)
        else:
            if self._on_result:
                call_in_main(self._on_result, result)
        finally:
            if self._on_finished:
                call_in_main(self._on_finished)


def run_async(
    fn: Callable[..., Any],
    *args,
    on_result: Callable[[Any], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
    on_progress: Callable[[Any], None] | None = None,
    on_finished: Callable[[], None] | None = None,
    **kwargs,
) -> Worker:
    worker = Worker(fn, args, kwargs, on_result, on_error, on_progress, on_finished)
    QThreadPool.globalInstance().start(worker)
    return worker
