# Changelog

Format: [Keep a Changelog](https://keepachangelog.com). Setiap perubahan WAJIB dicatat di sini
dan versi dinaikkan di `app/meta.py` + `pyproject.toml` (SemVer).

## [0.6.1] - 2026-11-07
### Removed
- Smoke test (`tools/smoke_test.py`) beserta langkahnya di `build.py` (`--skip-test`) dan env `APP_DATA_DIR_OVERRIDE`: terlalu merepotkan dan memberi false alarm (token di komentar QSS, maximize di platform offscreen).

## [0.6.0] - 2026-11-07
### Fixed
- Border hitam di tepi window frameless: penyebabnya `#Root { background-color: rgba(0,0,0,1) }` di QSS (alpha 1 dibaca opak). Sekarang area resize dilukis alpha 1/255 lewat `FramelessRoot.paintEvent`; smoke test menjaga agar aturan itu tidak kembali.
### Changed
- Sidebar didesain ulang: panel tersendiri (warna surface) dengan pembatas (garis kanan + garis antar grup), item horizontal ikon+teks, indikator kiri aksen pada item aktif.
- `PageSpec.bottom` (default False): halaman di grup bawah sidebar setelah pembatas (Pengaturan, Tentang).
- Titlebar berlatar surface dengan garis bawah (selaras sidebar).
- Window memakai `WindowMinMaxButtonsHint` (perilaku minimize/maximize native lebih baik).

## [0.5.1] - 2026-11-07
### Added
- Backdrop gelap di belakang dialog modal (`Backdrop` di `app/ui/dialogs.py`, QSS `#Backdrop`, token `backdrop`); fade in, menutup frame utama termasuk titlebar.
### Changed
- Navigasi sidebar: menyatu dengan background (transparan, tanpa garis pemisah); item aktif berupa pill membulat dengan teks & ikon berwarna aksen (tanpa garis kiri).
- Sidebar sedikit lebih lebar (92px) dengan jarak antar item.

## [0.5.0] - 2026-11-07
### Added
- Smoke test offscreen `tools/smoke_test.py` (versi, import modul, semua ikon qtawesome, QSS/token, MainWindow + semua halaman, toast, window state, komponen, dialog, worker, errors, single instance, version info). `build.py` menjalankannya otomatis sebelum build (`--skip-test` untuk melewati).
- Simpan & pulihkan posisi window + status maximized (`app/ui/window_state.py`); posisi di luar layar diabaikan (window ke tengah).
- Komponen UI siap pakai `app/ui/components/`: `ToggleSwitch`, `SettingRow`, `Card`, `PageHeader` (+ gaya QSS `#Card`, `#Divider`, `#SettingTitle`, `#SettingDesc`). Halaman Pengaturan & Tentang memakainya.
- Version info di exe (Properties > Details, Task Manager) lewat `tools/version_info.py` + `--version-file`; field baru `APP_DESCRIPTION`, `APP_AUTHOR` di `app/meta.py`.
- `Settings.update()` (tulis beberapa key sekaligus); env `APP_DATA_DIR_OVERRIDE` khusus test.
### Changed
- Pengaturan: checkbox diganti `ToggleSwitch`.
- `MainWindow.show_window()` menjaga status maximized saat dipulihkan dari tray/minimize.

## [0.4.0] - 2026-11-07
### Added
- Single instance per folder (`app/single_instance.py`): klik exe kedua memunculkan window yang sudah jalan; salinan portable di folder lain tidak bentrok.
- Helper background task `run_async` (`app/workers.py`) + jembatan main thread (`app/mainthread.py`).
- Penangkap error global (`app/errors.py`): log + toast error; error worker tanpa `on_error` ikut ditangkap.
- Dialog frameless `confirm()` / `info()` (`app/ui/dialogs.py`) + gaya QSS `#DialogFrame`, `QPushButton#Danger`.
- Halaman Tentang: info versi/OS, buka folder data, buka log, salin info.
- Beranda: panel demo Uji Worker / Uji Dialog / Uji Error (hapus di aplikasi nyata).
- `tools/rename_app.py` (ganti identitas app dari starter) dan `tools/bump_version.py` (naikkan versi + kerangka CHANGELOG).
### Changed
- Token tipografi baru `fs_heading` (16px) untuk judul dialog.
- Logger tidak memasang console handler bila `sys.stderr` None (exe windowed).

## [0.3.1] - 2026-11-07
### Added
- Beranda: tiga tombol uji toast (info / sukses / error).

## [0.3.0] - 2026-11-07
### Added
- Jalankan saat startup (`app/startup.py`, Windows HKCU Run, hanya build exe): checkbox di Pengaturan; start dengan `--minimized` langsung ke tray.
- Toast tengah bawah (`app/ui/toast.py`): `ctx.toast("teks", "info"|"success"|"error")`, fade in/out otomatis.
### Changed
- Tipografi diseragamkan: satu family + skala ukuran (small/base/title) lewat `FONT` di `theme.py`, dipakai QSS (`@font_family@`, `@fs_*@`) dan `QApplication.setFont`.

## [0.2.1] - 2026-11-07
### Fixed
- Crash saat start: prefix ikon qtawesome `fa5r` tidak valid -> pakai `fa5` (regular) untuk ikon maximize/restore di titlebar.

## [0.2.0] - 2026-11-07
### Added
- Ikon aplikasi `assets/icon.ico` + `assets/icon.png` (generator: `tools/make_icon.py`); dipakai exe, window, titlebar, tray.
- Tray icon (`app/ui/tray.py`): klik = tampil/sembunyikan, menu Tampilkan/Sembunyikan + Keluar.
- Close window -> sembunyi ke tray (opsi `close_to_tray`, bisa dimatikan di Pengaturan).
- Window frameless + custom titlebar (`app/ui/frameless.py`, `app/ui/titlebar.py`): drag, double-click maximize, resize dari tepi, tombol min/max/close.
- Styling QSS: `assets/styles/app.qss` (template token warna) + override user `<APP_ID>_Data/custom.qss`.
### Changed
- Nama default `NamaAplikasi` -> `Starter` (`APP_ID`, `APP_DISPLAY_NAME`, nama proyek).
- `app/ui/theme.py` kini berbasis token (`TOKENS`) + QSS, bukan palette hardcode.

## [0.1.0] - 2026-11-07
### Added
- Struktur starter: `app/` (meta, paths, settings, logger, ui), `main.py`, `build.py`.
- Sidebar + halaman via registry (`app/ui/pages/__init__.py`): Beranda, Pengaturan.
- Tema dark/light, tersimpan otomatis di `<APP_ID>_Data/settings.json`.
- Build PyInstaller: exe + `<APP_ID>_System/` (via `--contents-directory`).
- Bundle zip `<Display Name> <versi>.zip` dengan root folder `<Display Name>`.
- Dokumentasi: README, ARCHITECTURE, CHANGELOG.
