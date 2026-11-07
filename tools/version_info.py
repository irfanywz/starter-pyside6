"""Generator file version-info Windows untuk PyInstaller (--version-file). Stdlib only.

Properti ini tampil di Explorer (Properties > Details) dan Task Manager.
"""

import re
from datetime import date


def make_version_text(app_id: str, display_name: str, version: str, description: str, author: str) -> str:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        raise ValueError(f"Versi harus X.Y.Z, dapat: {version!r}")
    tup = tuple(int(x) for x in m.groups()) + (0,)
    dotted = ".".join(str(x) for x in tup)
    copyright_text = f"Copyright (c) {date.today().year} {author}".strip() if author else ""
    strings = [
        ("CompanyName", author),
        ("FileDescription", display_name),  # nama yang tampil di Task Manager
        ("FileVersion", dotted),
        ("InternalName", app_id),
        ("LegalCopyright", copyright_text),
        ("OriginalFilename", f"{app_id}.exe"),
        ("ProductName", display_name),
        ("ProductVersion", dotted),
        ("Comments", description),
    ]
    rows = ",\n          ".join(f"StringStruct({k!r}, {v!r})" for k, v in strings)
    return f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={tup!r},
    prodvers={tup!r},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
          {rows}
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
