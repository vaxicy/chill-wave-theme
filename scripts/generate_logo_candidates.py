#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chill Wave Theme - logo candidates (code-drawn, 128px).

Colors are read from manifest.json (never hardcoded).
Outputs relative paths -> store-assets/icon-candidates/
  a-triple-wave.png  b-moon-tide.png  c-ripple.png  d-wave-pulse.png
  preview.png        (side-by-side: 128 / 48 / 16 at 1:1 / 16 zoomed 4x)
"""
import json
import math
import os
import colorsys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)  # keep all save paths relative (Windows non-ASCII path + PIL save bug)

OUT = Path("store-assets/icon-candidates")
OUT.mkdir(parents=True, exist_ok=True)

MANIFEST = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
MCOL = MANIFEST["theme"]["colors"]
MTINT = MANIFEST["theme"]["tints"]

S = 6  # supersampling factor
R_RADIUS = 0.225  # corner radius ratio


def rgb(c):
    return tuple(int(v) for v in c)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, t):
    return mix(c, (0, 0, 0), t) if t > 0 else mix(c, (255, 255, 255), -t)


def tint(t):
    h, s, l = t
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (round(r * 255), round(g * 255), round(b * 255))


# palette derived from manifest
FRAME = rgb(MCOL["frame"])
FRAME_INC = rgb(MCOL["frame_incognito"])
TABBAR = rgb(MCOL["toolbar"])
TABBG = rgb(MCOL["background_tab"])
INK = rgb(MCOL["tab_text"])
LINK = rgb(MCOL["ntp_link"])
BTN = rgb(MCOL["button_background"])
FRAME_T = tint(MTINT["frame"])
WHITE = (255, 255, 255)


# ---------- drawing helpers ----------

def grad_at(stops, t):
    if t <= stops[0][0]:
        return stops[0][1]
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            k = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
            return tuple(round(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
    return stops[-1][1]


def vgrad(n, stops):
    img = Image.new("RGB", (n, n), stops[0][1])
    d = ImageDraw.Draw(img)
    for y in range(n):
        d.line([(0, y), (n, y)], fill=grad_at(stops, y / (n - 1)))
    return img


def wave_pts(n, y0, amp, wl, phase, step=2):
    pts = []
    x = 0
    while x <= n:
        y = y0 + amp * math.sin(2 * math.pi * x / wl + phase)
        pts.append((int(round(x)), int(round(y))))
        x += step
    if pts[-1][0] < n:
        y = y0 + amp * math.sin(2 * math.pi * n / wl + phase)
        pts.append((n, int(round(y))))
    return pts


def draw_wave_line(d, n, y0, amp, wl, phase, width, color):
    pts = wave_pts(n, y0, amp, wl, phase)
    w = max(1, round(width))
    d.line(pts, fill=color, width=w, joint="curve")
    r = w / 2
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)


def draw_wave_fill(d, n, y0, amp, wl, phase, color):
    pts = wave_pts(n, y0, amp, wl, phase)
    d.polygon(pts + [(n, n), (0, n)], fill=color)


def rounded_mask(size, radius_ratio=R_RADIUS):
    n = size * S
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, n - 1, n - 1],
                                        radius=round(n * radius_ratio), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def finalize(big, size):
    out = big.resize((size, size), Image.LANCZOS).convert("RGBA")
    out.putalpha(rounded_mask(size))
    return out


# ---------- schemes ----------

def scheme_a(size=128):
    """A. Triple Wave - three calm white waves on a violet gradient."""
    n = size * S
    big = vgrad(n, [(0.0, shade(FRAME, 0.06)), (0.55, FRAME), (1.0, mix(FRAME, FRAME_INC, 0.55))])
    d = ImageDraw.Draw(big)
    strokes = [
        (0.375, 0.050, 1.15, 0.00, 0.050, WHITE),
        (0.515, 0.058, 1.00, 1.15, 0.056, WHITE),
        (0.655, 0.044, 1.25, 2.30, 0.040, mix(FRAME, WHITE, 0.72)),
    ]
    for yy, aa, wl, ph, wd, col in strokes:
        draw_wave_line(d, n, yy * n, aa * n, wl * n, ph, wd * n, col)
    return finalize(big, size)


def scheme_b(size=128):
    """B. Moon Tide - crescent moon, stars and two tide layers."""
    n = size * S
    top = shade(LINK, 0.30)
    big = vgrad(n, [(0.0, top), (0.45, mix(top, FRAME, 0.45)), (1.0, mix(FRAME, FRAME_INC, 0.40))])
    # crescent moon mask
    moon = Image.new("L", (n, n), 0)
    md = ImageDraw.Draw(moon)
    cx, cy, r = 0.665 * n, 0.285 * n, 0.150 * n
    md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    bx, by, br = cx + 0.078 * n, cy - 0.062 * n, 0.134 * n
    md.ellipse([bx - br, by - br, bx + br, by + br], fill=0)
    big.paste((250, 250, 255), (0, 0), moon)
    d = ImageDraw.Draw(big)
    for sx, sy, sr in [(0.295, 0.200, 0.011), (0.195, 0.395, 0.008), (0.435, 0.145, 0.007)]:
        d.ellipse([(sx - sr) * n, (sy - sr) * n, (sx + sr) * n, (sy + sr) * n], fill=WHITE)
    draw_wave_fill(d, n, 0.640 * n, 0.052 * n, 1.05 * n, 0.60, mix(FRAME, WHITE, 0.22))
    draw_wave_fill(d, n, 0.780 * n, 0.058 * n, 0.95 * n, 2.50, mix(FRAME, WHITE, 0.58))
    return finalize(big, size)


def scheme_c(size=128):
    """C. Ripple - light porcelain base, concentric ripples + a soft sun."""
    n = size * S
    big = vgrad(n, [(0.0, mix(TABBAR, WHITE, 0.55)), (1.0, mix(TABBG, FRAME, 0.28))])
    d = ImageDraw.Draw(big)
    cx, cy = 0.5 * n, 0.845 * n
    rings = [
        (0.420, 0.040, mix(FRAME, WHITE, 0.58)),
        (0.320, 0.042, mix(FRAME, WHITE, 0.34)),
        (0.220, 0.044, FRAME),
        (0.118, 0.046, shade(FRAME, 0.12)),
    ]
    for rr, ww, col in rings:
        assert rr * n + ww * n / 2 < 0.5 * n, "ripple ring overflows canvas"
        d.arc([cx - rr * n, cy - rr * n, cx + rr * n, cy + rr * n],
              180, 360, fill=col, width=round(ww * n))
    sr = 0.090 * n
    d.ellipse([cx - sr, 0.245 * n - sr, cx + sr, 0.245 * n + sr], fill=shade(FRAME, 0.16))
    return finalize(big, size)


def scheme_d(size=128):
    """D. Wave Pulse - one bold white wave (best legibility at 16px)."""
    n = size * S
    big = vgrad(n, [(0.0, shade(FRAME, 0.32)), (0.50, shade(FRAME, 0.13)),
                    (1.0, mix(FRAME, FRAME_INC, 0.35))])
    d = ImageDraw.Draw(big)
    draw_wave_line(d, n, 0.580 * n, 0.112 * n, 1.30 * n, 0.00, 0.090 * n, WHITE)
    draw_wave_line(d, n, 0.762 * n, 0.068 * n, 1.05 * n, 1.00, 0.038 * n, mix(FRAME, WHITE, 0.70))
    return finalize(big, size)


# ---------- preview sheet ----------

def load_font(bold, size):
    name = "arialbd.ttf" if bold else "arial.ttf"
    for p in (f"C:/Windows/Fonts/{name}", name):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_preview(items):
    W, H, MARGIN, GAP = 1280, 408, 32, 24
    LOGO_Y, ROW_Y, ZOOM_SZ = 92, 232, 64
    ZOOM_Y = ROW_Y + 48 + 16
    col_w = (W - 2 * MARGIN - 3 * GAP) // 4
    assert 2 * MARGIN + 4 * col_w + 3 * GAP == W, "column math broken"
    bg = Image.new("RGB", (W, H), (221, 221, 229))
    d = ImageDraw.Draw(bg)
    f_name = load_font(True, 19)
    f_desc = load_font(False, 13)
    for i, (name, desc, img) in enumerate(items):
        x = MARGIN + i * (col_w + GAP)
        assert x + col_w <= W - MARGIN, "column overflows right margin"
        d.rounded_rectangle([x, 24, x + col_w, H - 24], radius=18, fill=(247, 247, 250))
        d.text((x + 20, 40), name, font=f_name, fill=INK)
        d.text((x + 20, 66), desc, font=f_desc, fill=shade(INK, -0.42))
        # 128 original
        big = img.resize((128, 128), Image.LANCZOS)
        bg.paste(big, (x + (col_w - 128) // 2, LOGO_Y), big)
        # 48 and 16 at 1:1, bottom-aligned, and 16 zoomed 4x
        s48 = img.resize((48, 48), Image.LANCZOS)
        s16 = img.resize((16, 16), Image.LANCZOS)
        zoom = s16.resize((ZOOM_SZ, ZOOM_SZ), Image.NEAREST)
        bg.paste(s48, (x + 22, ROW_Y), s48)
        bg.paste(s16, (x + 22 + 48 + 22, ROW_Y + 48 - 16), s16)
        bg.paste(zoom, (x + col_w - 22 - ZOOM_SZ, ZOOM_Y), zoom)
        d.text((x + 22 + 48 + 22 + 32, ROW_Y + 16), "48 / 16", font=f_desc,
               fill=shade(INK, -0.35))
        d.text((x + 22, ZOOM_Y + 8), "16px x4", font=f_desc, fill=shade(INK, -0.35))
        assert ZOOM_Y + ZOOM_SZ <= H - 24, "preview bottom overflow"
    bg.save(OUT / "preview.png")


def main():
    schemes = [
        ("A - Triple Wave", "three calm waves", scheme_a()),
        ("B - Moon Tide", "moon + tide layers", scheme_b()),
        ("C - Ripple", "concentric ripples", scheme_c()),
        ("D - Wave Pulse", "one bold wave", scheme_d()),
    ]
    for name, _desc, img in schemes:
        assert img.size == (128, 128), "logo must be 128x128"
        fname = name.split(" - ")[0].lower()
        slug = {"a": "a-triple-wave", "b": "b-moon-tide",
                "c": "c-ripple", "d": "d-wave-pulse"}[fname]
        img.save(OUT / f"{slug}.png")
    build_preview(schemes)
    print("done ->", OUT.as_posix())


if __name__ == "__main__":
    main()
