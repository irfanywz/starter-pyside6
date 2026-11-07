"""Build exe + bundle zip.  Jalankan: `uv run python build.py` (`--skip-test` untuk melewati smoke test)

Hasil (folder release/), contoh dengan APP_ID/APP_DISPLAY_NAME = "Starter":
    Starter <versi>.zip
    └── Starter/                 <- root tanpa versi
        ├── Starter.exe          <- ikon dari assets/icon.ico
        └── Starter_System/      <- = _internal milik PyInstaller
(Starter_Data/ dibuat otomatis saat aplikasi pertama dijalankan.)
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from app.meta import (  # noqa: E402
    APP_AUTHOR,
    APP_DESCRIPTION,
    APP_DISPLAY_NAME,
    APP_ID,
    APP_VERSION,
    SYSTEM_DIR_NAME,
)
from tools.version_info import make_version_text  # noqa: E402

BUILD = ROOT / "build"
DIST = BUILD / "dist"
RELEASE = ROOT / "release"


def check_version() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    if not m or m.group(1) != APP_VERSION:
        sys.exit(f"Versi tidak sama: pyproject={m.group(1) if m else '?'} meta={APP_VERSION}")


def run_smoke_test() -> None:
    print("== Smoke test ==")
    result = subprocess.run([sys.executable, str(ROOT / "tools" / "smoke_test.py")])
    if result.returncode != 0:
        sys.exit("Smoke test gagal; build dibatalkan (lewati dengan --skip-test).")


def write_version_file() -> Path:
    path = BUILD / "version_info.txt"
    BUILD.mkdir(parents=True, exist_ok=True)
    path.write_text(
        make_version_text(APP_ID, APP_DISPLAY_NAME, APP_VERSION, APP_DESCRIPTION, APP_AUTHOR),
        encoding="utf-8",
    )
    return path


def run_pyinstaller(version_file: Path) -> None:
    args = [
        str(ROOT / "main.py"),
        "--name", APP_ID,
        "--windowed",
        "--noconfirm",
        "--clean",
        "--contents-directory", SYSTEM_DIR_NAME,  # ganti nama _internal
        "--distpath", str(DIST),
        "--workpath", str(BUILD / "work"),
        "--specpath", str(BUILD),
        "--version-file", str(version_file),  # properti exe (Details)
        "--collect-data", "qtawesome",  # font ikon
        "--add-data", f"{ROOT / 'assets'}{os.pathsep}assets",
    ]
    icon = ROOT / "assets" / "icon.ico"
    if icon.exists():
        args += ["--icon", str(icon)]
    PyInstaller.__main__.run(args)


def make_zip() -> Path:
    src = DIST / APP_ID
    if not src.is_dir():
        sys.exit(f"Hasil build tidak ditemukan: {src}")
    RELEASE.mkdir(exist_ok=True)
    zip_path = RELEASE / f"{APP_DISPLAY_NAME} {APP_VERSION}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(src.rglob("*")):
            arc = Path(APP_DISPLAY_NAME) / f.relative_to(src)
            zf.write(f, arc)
    return zip_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Build exe + bundle zip")
    ap.add_argument("--skip-test", action="store_true", help="lewati smoke test")
    args = ap.parse_args()

    check_version()
    if not args.skip_test:
        run_smoke_test()
    if BUILD.exists():
        shutil.rmtree(BUILD)
    run_pyinstaller(write_version_file())
    z = make_zip()
    print(f"\nSelesai: {z}")


if __name__ == "__main__":
    main()
