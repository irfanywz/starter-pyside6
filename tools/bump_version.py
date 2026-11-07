"""Naikkan versi di app/meta.py + pyproject.toml sekaligus dan tambah kerangka entri CHANGELOG.

    uv run python tools/bump_version.py patch -m "Perbaiki crash di tray"
    uv run python tools/bump_version.py minor -m "Tambah halaman Laporan"
    uv run python tools/bump_version.py 1.0.0
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def replace_version(path: Path, pattern: str, new: str) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(pattern, text, re.M)
    if not m:
        sys.exit(f"Versi tidak ditemukan di {path}")
    old = m.group(2)
    path.write_text(
        text[: m.start()] + m.group(1) + new + m.group(3) + text[m.end():], encoding="utf-8"
    )
    return old


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("bump", help="patch | minor | major | X.Y.Z")
    ap.add_argument("-m", "--message", help="catatan perubahan untuk CHANGELOG")
    args = ap.parse_args()

    meta = ROOT / "app" / "meta.py"
    current = re.search(r'^APP_VERSION = "(\d+)\.(\d+)\.(\d+)"', meta.read_text(encoding="utf-8"), re.M)
    if not current:
        sys.exit("APP_VERSION tidak ditemukan / bukan format X.Y.Z")
    major, minor, patch = map(int, current.groups())

    if args.bump == "patch":
        new = f"{major}.{minor}.{patch + 1}"
    elif args.bump == "minor":
        new = f"{major}.{minor + 1}.0"
    elif args.bump == "major":
        new = f"{major + 1}.0.0"
    elif re.fullmatch(r"\d+\.\d+\.\d+", args.bump):
        new = args.bump
    else:
        sys.exit("Argumen harus patch | minor | major | X.Y.Z")

    old = replace_version(meta, r'(^APP_VERSION = ")([^"]+)(")', new)
    replace_version(ROOT / "pyproject.toml", r'(^version\s*=\s*")([^"]+)(")', new)

    changelog = ROOT / "CHANGELOG.md"
    note = args.message or "(isi catatan perubahan)"
    entry = f"## [{new}] - {date.today().isoformat()}\n### Changed\n- {note}\n\n"
    text = changelog.read_text(encoding="utf-8") if changelog.exists() else "# Changelog\n\n"
    idx = text.find("## [")
    text = text[:idx] + entry + text[idx:] if idx != -1 else text.rstrip() + "\n\n" + entry
    changelog.write_text(text, encoding="utf-8")

    print(f"Versi {old} -> {new}")
    if not args.message:
        print("Edit CHANGELOG.md: ganti placeholder & sesuaikan kategori (Added/Changed/Fixed).")


if __name__ == "__main__":
    main()
