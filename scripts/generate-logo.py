#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chill Wave Theme - final logo (128x128) -> logo/logo.png

Design: "Moon Tide" - crescent moon, stars and two soft tide layers.
Colors are read from manifest.json (single source of truth), never hardcoded.
Re-runnable: always overwrites logo/logo.png.
"""
import json
import math
import os
import colorsys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)  # relative save paths only (Windows non-ASCII path + PIL save bug)

MANIFEST = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
MCOL = MANIFEST["theme"]["colors"]
MTINT = MANIFEST["theme"]["tints"]

SIZE = 128
S = 6              # supersampling factor
R_RADIUS = 0.225   # corner radius ratio
WHITE = (255, 255, 255)


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


FRAME = rgb(MCOL["frame"])            # #A09BD9 main violet
FRAME_INC = rgb(MCOL["frame_incognito"])
LINK = rgb(MCOL["ntp_link"])          # deep blue accent


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


def draw_wave_fill(d, n, y0, amp, wl, phase, color):
    d.polygon(wave_pts(n, y0, amp, wl, phase) + [(n, n), (0, n)], fill=color)


def rounded_mask(size, radius_ratio=R_RADIUS):
    n = size * S
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, n - 1, n - 1],
                                        radius=round(n * radius_ratio), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def build_logo(size=SIZE):
    n = size * S
    top = shade(LINK, 0.30)
    big = vgrad(n, [(0.0, top),
                    (0.45, mix(top, FRAME, 0.45)),
                    (1.0, mix(FRAME, FRAME_INC, 0.40))])

    # crescent moon (mask trick: moon disc minus an offset disc)
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

    out = big.resize((size, size), Image.LANCZOS).convert("RGBA")
    out.putalpha(rounded_mask(size))
    return out


def main():
    assert not MTINT.get("frame_inactive") is None, "manifest tints missing"
    Path("logo").mkdir(exist_ok=True)
    logo = build_logo()
    assert logo.size == (128, 128), "logo must be 128x128"
    logo.save("logo/logo.png")
    print("done -> logo/logo.png (128x128, Moon Tide)")


if __name__ == "__main__":
    main()