"""Smoke test offscreen: menangkap error umum (nama ikon salah, QSS rusak, halaman crash) sebelum build.

    uv run python tools/smoke_test.py

Memakai folder data sementara (tidak menyentuh <APP_ID>_Data). Exit code 1 bila ada yang gagal.
`build.py` menjalankan ini otomatis (lewati dengan --skip-test).
"""

import os
import re
import sys
import tempfile
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["APP_DATA_DIR_OVERRIDE"] = tempfile.mkdtemp(prefix="smoke_")

import importlib  # noqa: E402
import pkgutil  # noqa: E402

import qtawesome as qta  # noqa: E402
from PySide6.QtCore import QRect  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

failures: list[str] = []


def check(name: str, fn) -> None:
    try:
        fn()
        print(f"  ok    {name}")
    except Exception as exc:  # noqa: BLE001
        failures.append(name)
        print(f"  FAIL  {name}: {exc!r}")
        traceback.print_exc()


def pump(app, seconds: float = 0.05) -> None:
    end = time.time() + seconds
    while time.time() < end:
        app.processEvents()
        time.sleep(0.005)


def main() -> int:
    app = QApplication(sys.argv)

    import app as app_pkg
    from app import errors, mainthread
    from app.meta import APP_VERSION
    from app.paths import ensure_dirs
    from app.settings import Settings
    from app.single_instance import SingleInstance
    from app.ui import theme, window_state
    from app.ui.components import Card, PageHeader, SettingRow, ToggleSwitch
    from app.ui.dialogs import AppDialog, Backdrop
    from app.ui.main_window import AppContext, MainWindow
    from app.workers import run_async
    from tools.version_info import make_version_text

    ensure_dirs()
    mainthread.init()
    print("Smoke test")

    def versions_match():
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
        assert m and m.group(1) == APP_VERSION, f"pyproject={m and m.group(1)} meta={APP_VERSION}"
        assert re.fullmatch(r"\d+\.\d+\.\d+", APP_VERSION), "APP_VERSION harus X.Y.Z"

    def imports_ok():
        for mod in pkgutil.walk_packages(app_pkg.__path__, "app."):
            importlib.import_module(mod.name)

    def icons_ok():
        names = set()
        for f in (ROOT / "app").rglob("*.py"):
            names.update(re.findall(r"""["'](fa5[sb]?\.[a-z0-9-]+)["']""", f.read_text(encoding="utf-8")))
        assert names, "tidak ada ikon ditemukan (regex rusak?)"
        for n in sorted(names):
            qta.icon(n)  # error bila nama/prefix tidak valid

    def qss_ok():
        assert set(theme.TOKENS["dark"]) == set(theme.TOKENS["light"]), "token dark/light tidak sama"
        template = (ROOT / "assets" / "styles" / "app.qss").read_text(encoding="utf-8")
        assert not re.search(r"#Root\s*\{[^}]*rgba", template), "#Root tidak boleh pakai rgba di QSS (border hitam)"
        for name in ("dark", "light"):
            out = theme._render(template, {**theme.tokens(name), **theme.FONT})
            left = set(re.findall(r"@[a-z_]+@", out))
            assert not left, f"token QSS tidak terdefinisi ({name}): {left}"
            theme.apply_theme(app, name)

    check("versi pyproject == meta", versions_match)
    check("semua modul bisa di-import", imports_ok)
    check("semua ikon qtawesome valid", icons_ok)
    check("QSS & token (dark/light)", qss_ok)

    settings = Settings()
    theme.apply_theme(app, "dark")
    ctx = AppContext(app, settings)
    holder = {}

    def window_ok():
        win = MainWindow(ctx)
        holder["win"] = win
        win.show()
        pump(app)
        for i in range(win.stack.count()):
            win.group.button(i).click()
            pump(app)
        ctx.toast("tes", "success")
        pump(app)
        assert win.toaster.isVisible(), "toast tidak tampil"
        win.showMaximized()
        pump(app)
        if win.isMaximized():  # platform offscreen bisa saja tidak mendukung maximize
            assert win.frame.property("maximized") is True
        win.showNormal()
        pump(app)
        assert win.frame.property("maximized") is False

    def window_state_ok():
        win = holder["win"]
        window_state.save(win, settings)
        for key in ("window_width", "window_height", "window_x", "window_y"):
            assert isinstance(settings.get(key), int), key
        assert not window_state._visible(QRect(-10000, -10000, 800, 600)), "posisi di luar layar harus ditolak"
        assert window_state._visible(QRect(0, 0, 800, 600)), "posisi normal harus diterima"

    def components_ok():
        sw = ToggleSwitch(False)
        sw.setChecked(True)
        assert sw.isChecked()
        pump(app, 0.25)
        assert sw.offset > 0.9, "animasi switch tidak berjalan"
        card = Card("T")
        card.add(SettingRow("Judul", "Deskripsi", ToggleSwitch()))
        card.add_divider()
        PageHeader("Judul", "Sub")

    def dialog_ok():
        dlg = AppDialog(holder["win"], "Judul", "Pesan")
        dlg.add_button("OK", accept=True, name="Primary", default=True)
        dlg.adjustSize()
        win = holder["win"]
        backdrop = Backdrop.create(win)
        assert backdrop is not None and backdrop.geometry() == win.frame.rect(), "backdrop tidak menutup frame"
        backdrop.dismiss()

    def worker_ok():
        got = {}
        run_async(lambda: 41 + 1, on_result=lambda r: got.setdefault("r", r), on_finished=lambda: got.setdefault("f", True))
        end = time.time() + 3
        while "f" not in got and time.time() < end:
            pump(app, 0.02)
        assert got.get("r") == 42 and got.get("f"), f"worker tidak selesai: {got}"

    def errors_ok():
        seen = []
        errors.install(seen.append)
        errors.notify(ValueError("x"))
        pump(app)
        assert seen and "x" in seen[0]

    def single_instance_ok():
        first, second = SingleInstance(), SingleInstance()
        assert first.try_acquire() is True
        assert second.try_acquire() is False

    def version_info_ok():
        text = make_version_text("App", "App Name", "1.2.3", "desc", "Author")

        class _Any:
            def __init__(self, *a, **k):
                pass

        ns = {n: _Any for n in (
            "VSVersionInfo", "FixedFileInfo", "StringFileInfo", "StringTable",
            "StringStruct", "VarFileInfo", "VarStruct",
        )}
        exec(compile(text, "version_info", "exec"), ns)  # sintaks valid
        assert "(1, 2, 3, 0)" in text

    check("MainWindow + semua halaman + toast + maximize", window_ok)
    check("window_state (simpan & validasi posisi)", window_state_ok)
    check("komponen UI", components_ok)
    check("dialog", dialog_ok)
    check("worker (run_async)", worker_ok)
    check("errors.notify", errors_ok)
    check("single instance", single_instance_ok)
    check("version info exe", version_info_ok)

    win = holder.get("win")
    if win is not None:
        ctx.quitting = True
        win.tray.hide()
        win.close()

    if failures:
        print(f"\n{len(failures)} GAGAL: {', '.join(failures)}")
        return 1
    print("\nSemua OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
