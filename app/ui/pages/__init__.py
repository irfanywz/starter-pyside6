"""REGISTRY HALAMAN. Menambah halaman = buat file page + daftarkan di PAGES.

Urutan di PAGES = urutan di sidebar. `bottom=True` = ditaruh di grup bawah (setelah pembatas).
"""

from dataclasses import dataclass
from typing import Callable

from .about_page import AboutPage
from .base_page import BasePage
from .home_page import HomePage
from .settings_page import SettingsPage


@dataclass(frozen=True)
class PageSpec:
    key: str                          # id unik
    title: str                        # label sidebar
    icon: str                         # nama ikon qtawesome (mis. "fa5s.home")
    factory: Callable[..., BasePage]  # dipanggil dengan ctx
    bottom: bool = False              # True = grup bawah sidebar


PAGES: list[PageSpec] = [
    PageSpec("home", "Beranda", "fa5s.home", HomePage),
    PageSpec("settings", "Pengaturan", "fa5s.cog", SettingsPage, bottom=True),
    PageSpec("about", "Tentang", "fa5s.info-circle", AboutPage, bottom=True),
]
