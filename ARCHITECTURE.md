# ARCHITECTURE

Dokumen ini ditulis agar developer/agent AI lain cepat paham. Update setiap struktur berubah.
`<APP_ID>` = nilai `APP_ID` di `app/meta.py` (default `Starter`). Target: aplikasi desktop **portable** (Windows).

## Stack
Python >=3.10 (uv) · PySide6 >=6.6 · qtawesome >=1.3 · PyInstaller >=6.0 (dev group).
Tanpa package build: `[tool.uv] package = false`, jalankan dari root proyek.

## Struktur folder
```
main.py                 entry point (urutan start: lihat "Alur start")
build.py                PyInstaller + zip bundle (cek versi pyproject == meta)
pyproject.toml          dependency (uv), versi
tools/
  make_icon.py          generator ikon default (stdlib) -> assets/icon.ico + icon.png
  version_info.py       generator file version-info Windows untuk PyInstaller
  rename_app.py         ganti APP_ID / nama tampilan / nama proyek (+ reset versi & CHANGELOG)
  bump_version.py       naikkan versi di meta.py + pyproject.toml + kerangka entri CHANGELOG
assets/
  icon.ico, icon.png    ikon exe (ico) & ikon window/tray/titlebar (png)
  styles/app.qss        template QSS dengan token @warna@ / @font@
app/
  meta.py               APP_ID, APP_DISPLAY_NAME, APP_VERSION, nama folder Data/System (SATU sumber nama & versi)
  paths.py              BASE_DIR, DATA_DIR, LOG_DIR, SETTINGS_FILE, CUSTOM_QSS, ICON_PNG, QSS_FILE, resource_path(), ensure_dirs()
  settings.py           Settings: JSON di DATA_DIR, get/set, simpan atomic otomatis (DEFAULTS di file ini)
  logger.py             logging ke DATA_DIR/logs/app.log (rotating) + console (bila ada stderr)
  startup.py            jalankan saat startup (winreg HKCU Run, hanya frozen+Windows; flag --minimized)
  single_instance.py    SingleInstance (QLocalServer/Socket), kunci = APP_ID + hash BASE_DIR (per folder)
  mainthread.py         call_in_main(fn, ...) : jembatan thread -> main thread; init() dari main.py
  workers.py            run_async(fn, on_result/on_error/on_progress/on_finished) di QThreadPool
  errors.py             excepthook global (sys + threading): log + toast error; notify(exc)
  ui/
    main_window.py      AppContext + MainWindow (frameless, sidebar + QStackedWidget, tray, toast, logika close)
    frameless.py        FramelessRoot: margin transparan = zona resize (startSystemResize)
    titlebar.py         TitleBar: drag (startSystemMove), double-click maximize, tombol min/max/close
    tray.py             AppTray: QSystemTrayIcon + menu Tampilkan/Sembunyikan/Keluar
    toast.py            Toast: notifikasi tengah bawah (child AppFrame, fade); dipakai via ctx.toast()
    dialogs.py          AppDialog, confirm(), info(): dialog frameless modal (pengganti QMessageBox)
    window_state.py     simpan/pulihkan ukuran, posisi, maximized (posisi di luar layar diabaikan)
    components/         ToggleSwitch, SettingRow, Card, PageHeader (komponen siap pakai, gaya via QSS)
    theme.py            TOKENS (warna dark/light), FONT (tipografi), apply_theme(): palette + font + QSS + custom.qss
    pages/
      __init__.py       PAGES: registry halaman (urutan = urutan sidebar)
      base_page.py      BasePage (hook on_show)
      home_page.py      Beranda + panel DEMO (toast/worker/dialog/error) -> hapus di aplikasi nyata
      settings_page.py  tema, tutup ke tray, jalankan saat startup
      about_page.py     info versi/OS, buka folder data, buka log, salin info
```

## Alur start (`main.py`)
`ensure_dirs` -> `setup_logging` -> `QApplication` -> `mainthread.init()` -> `SingleInstance.try_acquire()`
(gagal = instance lain jalan, sudah diberi sinyal, keluar) -> `Settings` -> `apply_theme` -> `AppContext` -> `MainWindow`
-> `instance.activated -> win.show_window` -> `errors.install(toast)` -> `startup.sync()` -> tampilkan window
(kecuali flag `--minimized` dan tray siap) -> `app.exec()`.

## Alur window (frameless)
`MainWindow` (Qt.FramelessWindowHint + WA_TranslucentBackground)
-> `FramelessRoot` (#Root, margin 6px transparan = area resize; margin 0 saat maximized)
-> `QFrame#AppFrame` (border + rounded, property `maximized` dipakai QSS)
-> `TitleBar` + body (`#Sidebar` + `QStackedWidget#Pages`).
Event `WindowStateChange` memperbarui property `maximized`, margin root, dan ikon tombol max/restore.

## Tray, close, single instance
- Tray aktif bila `QSystemTrayIcon.isSystemTrayAvailable()`.
- `closeEvent`: jika setting `close_to_tray` true dan tray siap -> `hide()` (aplikasi tetap jalan). Keluar sungguhan lewat menu tray "Keluar" (`MainWindow.quit_app`, set `ctx.quitting`).
- `QApplication.setQuitOnLastWindowClosed(False)` di `main.py`; `closeEvent` memanggil `app.quit()` saat benar-benar keluar.
- Single instance per folder: exe kedua mengirim sinyal ke yang pertama lalu keluar; yang pertama memanggil `show_window()`.

## Threading & error
- Kerja berat: `run_async(fn, ...)` (QThreadPool). Callback selalu di main thread via `mainthread.call_in_main`. Fungsi worker tidak boleh menyentuh widget. Parameter `progress` pada fungsi worker bersifat opsional.
- Exception tak tertangani (main thread, thread lain, slot Qt) -> `errors._excepthook` -> log + toast error. Error worker tanpa `on_error` -> `errors.notify`.

## Dialog & toast
- `ctx.toast(text, kind="info"|"success"|"error", ms=2500)` (diganti `Toast.show_message` oleh `MainWindow`). Posisi tengah bawah `AppFrame` (`reposition()` di `resizeEvent`).
- `confirm(parent, title, message, ok_text, cancel_text, danger)` -> bool; `info(...)`. Parent = `self.window()`. Saat tampil, `Backdrop` (QSS `#Backdrop`, token `backdrop`) menggelapkan `MainWindow.backdrop_target()` (= `AppFrame`). Gaya: `#DialogFrame #DialogTitle #DialogMessage`, tombol `#Primary` / `#Danger`.

## Startup
- Sumber kebenaran = registry (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run\<APP_ID>`), bukan settings.json. Perintah: `"<exe>" --minimized`.
- `startup.sync()` memperbarui path jika exe dipindah (portable). Di dev (bukan frozen) checkbox nonaktif.

## Komponen UI (`app/ui/components`)
- `ToggleSwitch(checked)` (sinyal `toggled`; warna dari palette: Highlight/Mid), `SettingRow(title, desc, control)`, `Card(title)` (+ `.add()`, `.add_divider()`), `PageHeader(title, subtitle)`.
- Halaman baru sebaiknya disusun dari komponen ini agar tampilan seragam; contoh: `settings_page.py`, `about_page.py`.

## Window state
`window_state.restore()` di `MainWindow.__init__` (ukuran, posisi, maximized); `window_state.save()` di `closeEvent` (baik hide ke tray maupun keluar). Posisi tersimpan yang tak terlihat di layar mana pun diabaikan.

## Version info exe
Dibuat saat build oleh `tools/version_info.py` dari `app/meta.py` (`APP_ID`, `APP_DISPLAY_NAME`, `APP_VERSION`, `APP_DESCRIPTION`, `APP_AUTHOR`) lewat `--version-file`.

## Styling (QSS)
- Warna dikelola di `TOKENS`, tipografi di `FONT` (`theme.py`); QSS memakai placeholder `@token@`.
- Urutan: `assets/styles/app.qss` lalu `<APP_ID>_Data/custom.qss` (override user, tanpa rebuild).
- Chrome (titlebar + sidebar) = panel `surface` dengan pembatas 1px; konten = `bg`. Sidebar: item `QPushButton` horizontal (ikon+teks), aktif = indikator kiri aksen + latar `accent_soft`; grup atas/bawah dipisah `#NavDivider` (atur lewat `PageSpec.bottom`). Ikon aktif memakai `color_on` qtawesome (`MainWindow._refresh_icons`).
- JANGAN beri `#Root` warna rgba di QSS: Qt membaca alpha 1 sebagai opak (border hitam). Piksel alpha 1/255 untuk area resize dilukis di `FramelessRoot.paintEvent`.
- Targetkan widget lewat objectName: `#Root #AppFrame #TitleBar #TitleLabel #TitleBtn #CloseBtn #Sidebar #Pages #Toast #DialogFrame`, `QLabel#PageTitle`, `QLabel#Muted`, `QPushButton#Primary`, `QPushButton#Danger`.
- Tipografi: SATU family + skala `fs_small / fs_base / fs_heading / fs_title`; jangan tulis font-family/ukuran acak di QSS/widget, pakai `@font_family@` dan `@fs_*@`.
- Ikon qtawesome tidak bisa diatur QSS; warnanya dari `icon_color()` dan di-refresh saat `theme_changed`. Prefix qtawesome: `fa5s` (solid), `fa5` (regular), `fa5b` (brands).
- Menambah warna: tambah key di kedua tema pada `TOKENS`, pakai `@key@` di QSS.

## Konvensi
- Nama & versi hanya di `app/meta.py` (+ `pyproject.toml` untuk versi; build.py memvalidasi keduanya sama). Naikkan versi lewat `tools/bump_version.py`.
- Semua path lewat `app/paths.py`; jangan hardcode. Semua data tulis ke `DATA_DIR` (portable: tidak menulis di luar folder, kecuali opsi startup).
- Halaman menerima `ctx: AppContext` (settings, app, toast, sinyal `theme_changed`). Logika bisnis jangan di widget besar; buat modul sendiri di `app/` (mis. `app/services/`) bila tumbuh.
- UI minimalis: sedikit input, simpan otomatis, tanpa form panjang. Styling lewat QSS, bukan `setStyleSheet` inline. Dialog lewat `app/ui/dialogs.py`, bukan `QMessageBox`.
- Menambah halaman: buat `app/ui/pages/xxx_page.py` (turunan `BasePage`), daftarkan `PageSpec` di `PAGES`.
- Dependency tidak memakai "latest"; tulis versi/rentang eksplisit.
- Setiap perubahan: catat `CHANGELOG.md` + naikkan versi.

## Lokasi data & build
| Mode | BASE_DIR | DATA_DIR | Bundel |
|------|----------|----------|--------|
| Dev | root proyek | `<root>/<APP_ID>_Data` | `<root>/assets` |
| Frozen | folder `.exe` | `<folder exe>/<APP_ID>_Data` | `<APP_ID>_System/` (`sys._MEIPASS`) |

`<APP_ID>_System` didapat dari opsi PyInstaller `--contents-directory` (setara rename `_internal`), jadi `sys._MEIPASS` otomatis menunjuk ke sana. `assets/` ikut dibundel lewat `--add-data`.

## Output build (`uv run python build.py`)
1. PyInstaller (onedir, windowed, `--icon assets/icon.ico`) -> `build/dist/<APP_ID>/`
2. Zip -> `release/<APP_DISPLAY_NAME> <versi>.zip`, root di dalam zip `<APP_DISPLAY_NAME>/` (tanpa versi):
```
<APP_DISPLAY_NAME>/
├── <APP_ID>.exe
└── <APP_ID>_System/
```
`<APP_ID>_Data/` tidak ikut zip; dibuat saat first run oleh `ensure_dirs()`.
`build/` dan `release/` di-gitignore.
