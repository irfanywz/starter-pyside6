# Starter (PySide6)

Base utama untuk semua aplikasi GUI PySide6: struktur folder, build, dan dokumentasi seragam.
Dirancang **portable**: semua data di folder `<APP_ID>_Data` di samping exe.

Fitur bawaan: window frameless + custom titlebar, tray (close = sembunyi ke tray), single instance,
jalankan saat startup (opsional), toast, dialog konfirmasi, background worker, penangkap error global,
halaman Tentang, posisi window tersimpan, komponen UI (switch, card, setting row), version info di exe, smoke test, tema dark/light berbasis QSS, ikon, settings otomatis tersimpan.

## Jalankan (dev)
```bash
uv sync
uv run python main.py
```

## Membuat aplikasi baru dari starter
```bash
# 1. salin folder starter, lalu di folder salinan:
uv run python tools/rename_app.py MyApp "My App"   # ganti APP_ID, nama tampilan, nama proyek, reset versi & CHANGELOG
uv sync
# 2. ganti assets/icon.ico + assets/icon.png dengan ikon sendiri
# 3. hapus panel demo di app/ui/pages/home_page.py, tambah halaman di app/ui/pages/ (daftarkan di PAGES)
```

## Alur kerja harian
```bash
uv run python tools/bump_version.py patch -m "Perbaiki ..."   # patch | minor | major | X.Y.Z
# lalu rapikan entri CHANGELOG.md bila perlu
uv run python build.py
```

## Build exe + zip
```bash
uv run python build.py              # menjalankan smoke test dulu
uv run python build.py --skip-test  # lewati smoke test
uv run python tools/smoke_test.py   # smoke test saja
```
Hasil: `release/Starter <versi>.zip`
```
Starter/
├── Starter.exe              # ikon dari assets/icon.ico
└── Starter_System/          # isi PyInstaller (pengganti _internal)
```
Saat dijalankan, `Starter_Data/` dibuat otomatis di samping exe (settings, log, semua data).
Nama mengikuti `APP_ID` / `APP_DISPLAY_NAME` di `app/meta.py`.

## Portable
- Semua data aplikasi ada di `<APP_ID>_Data` di samping exe; menyalin/memindah folder = memindah semuanya.
- Single instance dihitung per folder, jadi dua salinan di folder berbeda bisa jalan bersamaan.
- Satu-satunya yang menulis di luar folder adalah opsi "Jalankan saat startup" (registry HKCU Run, opsional, default mati). Path-nya diperbarui otomatis jika folder dipindah.

## Pola yang sering dipakai
```python
ctx.toast("Tersimpan", "success")                              # "info" | "success" | "error"

from app.ui.dialogs import confirm, info
if confirm(self.window(), "Hapus?", "Data akan hilang.", ok_text="Hapus", danger=True): ...

from app.workers import run_async                              # kerja berat di background
run_async(fungsi_berat, on_result=lambda r: ctx.toast("Selesai", "success"))
```

## Komponen UI
```python
from app.ui.components import Card, PageHeader, SettingRow, ToggleSwitch
card = Card("Umum")
card.add(SettingRow("Mode gelap", "Ganti tema", ToggleSwitch(True)))
```

## Properti exe
Nama, versi, deskripsi, dan author yang tampil di Properties > Details diambil dari `app/meta.py`
(`APP_DISPLAY_NAME`, `APP_VERSION`, `APP_DESCRIPTION`, `APP_AUTHOR`).

## Kustom tampilan
- Edit `assets/styles/app.qss` (warna lewat token `@nama@`, definisi di `app/ui/theme.py`).
- Atau tanpa build ulang: buat `Starter_Data/custom.qss`, dimuat terakhir dan menimpa style bawaan.

Baca `ARCHITECTURE.md` untuk detail struktur.
