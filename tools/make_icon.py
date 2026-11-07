"""Generator ikon default (stdlib only, tanpa Pillow).

Jalankan: `uv run python tools/make_icon.py`
Hasil   : assets/icon.ico (multi-size, dipakai exe) + assets/icon.png (256px, dipakai window/tray).
Ingin ikon sendiri? Cukup timpa kedua file itu; tidak perlu menjalankan skrip ini.
"""

import struct
import zlib
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SIZES = [16, 24, 32, 48, 64, 128, 256]
SS = 3  # supersampling per sumbu (anti-alias)

C1 = (61, 126, 255)   # gradient atas-kiri
C2 = (122, 77, 255)   # gradient bawah-kanan
WHITE = (255, 255, 255)


def sd_round_rect(x, y, cx, cy, hw, hh, r):
    qx = abs(x - cx) - (hw - r)
    qy = abs(y - cy) - (hh - r)
    ox, oy = max(qx, 0.0), max(qy, 0.0)
    return (ox * ox + oy * oy) ** 0.5 + min(max(qx, qy), 0.0) - r


def sample(u, v):
    """Return (r, g, b, a) float 0..1 di koordinat unit (u, v)."""
    # background rounded square + gradient
    if sd_round_rect(u, v, 0.5, 0.5, 0.47, 0.47, 0.22) > 0:
        return 0.0, 0.0, 0.0, 0.0
    t = (u + v) / 2
    r, g, b = (C1[i] + (C2[i] - C1[i]) * t for i in range(3))
    # jendela putih: outline + titlebar + divider sidebar
    wx, wy, hw, hh = 0.5, 0.52, 0.29, 0.24
    sd = sd_round_rect(u, v, wx, wy, hw, hh, 0.06)
    top, left = wy - hh, wx - hw
    white = False
    if -0.045 <= sd <= 0:
        white = True
    elif sd < -0.045:
        if v < top + 0.10:
            white = True
        elif abs(u - (left + 0.14)) < 0.018 and v > top + 0.10:
            white = True
    if white:
        r, g, b = WHITE
    return r, g, b, 1.0


def render(n):
    rows = []
    for py in range(n):
        row = bytearray([0])  # filter type 0
        for px in range(n):
            ar = ag = ab = aa = 0.0
            for sy in range(SS):
                for sx in range(SS):
                    r, g, b, a = sample((px + (sx + .5) / SS) / n, (py + (sy + .5) / SS) / n)
                    ar += r * a; ag += g * a; ab += b * a; aa += a
            cnt = SS * SS
            if aa > 0:
                row += bytes((round(ar / aa), round(ag / aa), round(ab / aa), round(255 * aa / cnt)))
            else:
                row += bytes(4)
        rows.append(bytes(row))
    return b"".join(rows)


def png_bytes(n):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(render(n), 9))
        + chunk(b"IEND", b"")
    )


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    images = {n: png_bytes(n) for n in SIZES}
    (ASSETS / "icon.png").write_bytes(images[256])

    header = struct.pack("<HHH", 0, 1, len(SIZES))
    offset = 6 + 16 * len(SIZES)
    entries, blobs = b"", b""
    for n in SIZES:
        data = images[n]
        entries += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    (ASSETS / "icon.ico").write_bytes(header + entries + blobs)
    print("OK:", ASSETS / "icon.ico", ASSETS / "icon.png")


if __name__ == "__main__":
    main()
