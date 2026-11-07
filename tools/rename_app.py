"""Ganti identitas aplikasi dari starter (jalankan sekali setelah menyalin folder starter).

    uv run python tools/rename_app.py MyApp "My App"
    uv run python tools/rename_app.py MyApp              # nama tampilan = MyApp

Mengubah: app/meta.py (APP_ID, APP_DISPLAY_NAME), pyproject.toml (name), README.md,
dan (default) mereset versi ke 0.1.0 + CHANGELOG baru. Pakai --keep-history untuk menahan keduanya.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sub_line(text: str, pattern: str, value: str) -> str:
    new, n = re.subn(pattern, lambda m: m.group(1) + value + m.group(2), text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"Pola tidak ditemukan: {pattern}")
    return new


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("app_id", help="tanpa spasi, mis. MyApp (nama exe & prefix folder)")
    ap.add_argument("display_name", nargs="?", help="nama tampilan (boleh spasi)")
    ap.add_argument("--keep-history", action="store_true", help="jangan reset versi & CHANGELOG")
    args = ap.parse_args()

    app_id = args.app_id
    display = args.display_name or app_id
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", app_id):
        sys.exit("app_id hanya huruf/angka/underscore, tanpa spasi, diawali huruf")
    if any(c in display for c in '"\\'):
        sys.exit('display_name tidak boleh mengandung " atau \\')
    slug = app_id.lower().replace("_", "-")

    meta_path = ROOT / "app" / "meta.py"
    meta = meta_path.read_text(encoding="utf-8")
    old_id = re.search(r'^APP_ID = "([^"]+)"', meta, re.M).group(1)
    old_display = re.search(r'^APP_DISPLAY_NAME = "([^"]+)"', meta, re.M).group(1)

    meta = sub_line(meta, r'(^APP_ID = ")[^"]+(")', app_id)
    meta = sub_line(meta, r'(^APP_DISPLAY_NAME = ")[^"]+(")', display)
    if not args.keep_history:
        meta = sub_line(meta, r'(^APP_VERSION = ")[^"]+(")', "0.1.0")
    meta_path.write_text(meta, encoding="utf-8")

    py_path = ROOT / "pyproject.toml"
    py = py_path.read_text(encoding="utf-8")
    py = sub_line(py, r'(^name = ")[^"]+(")', slug)
    if not args.keep_history:
        py = sub_line(py, r'(^version = ")[^"]+(")', "0.1.0")
    py_path.write_text(py, encoding="utf-8")

    readme = ROOT / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        text = text.replace(old_display, display).replace(old_id, app_id)
        readme.write_text(text, encoding="utf-8")

    if not args.keep_history:
        from datetime import date

        (ROOT / "CHANGELOG.md").write_text(
            "# Changelog\n\n"
            "Format: [Keep a Changelog](https://keepachangelog.com). Setiap perubahan WAJIB dicatat di sini\n"
            "dan versi dinaikkan (`uv run python tools/bump_version.py ...`).\n\n"
            f"## [0.1.0] - {date.today().isoformat()}\n"
            f"### Added\n- Proyek {display} dibuat dari starter PySide6.\n",
            encoding="utf-8",
        )

    print(f"OK: {old_id} -> {app_id} | '{old_display}' -> '{display}' | project '{slug}'")
    print("Langkah berikut: uv sync, ganti assets/icon.ico & icon.png, lalu uv run python main.py")


if __name__ == "__main__":
    main()
