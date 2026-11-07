"""Identitas aplikasi. SATU-SATUNYA tempat mengganti nama & versi.

Saat membuat aplikasi baru dari starter ini, ubah file ini + pyproject.toml.
"""

APP_ID = "Starter"            # tanpa spasi: nama exe & prefix folder
APP_DISPLAY_NAME = "Starter"  # tampil di UI, nama zip & root folder zip (boleh pakai spasi)
APP_VERSION = "0.6.0"         # samakan dengan pyproject.toml

APP_DESCRIPTION = "Aplikasi desktop PySide6"  # properti file exe (Comments)
APP_AUTHOR = ""                              # properti file exe (Company); kosongkan bila tak perlu

DATA_DIR_NAME = f"{APP_ID}_Data"      # semua data user/aplikasi
SYSTEM_DIR_NAME = f"{APP_ID}_System"  # isi PyInstaller (_internal di-rename)
