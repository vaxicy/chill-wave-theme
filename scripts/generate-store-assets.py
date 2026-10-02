#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chill Wave Theme - store artwork composer (single source of truth).

Renders 4 assets from HTML/CSS with headless Chromium (Playwright):
  store-assets/references/screenshot-1-browser.png     1280x800  full-window mockup
  store-assets/references/screenshot-2-introduction.png 1280x800  intro + color cards
  store-assets/references/promo-440x280.png             440x280  brand tile
  store-assets/references/promo-1400x560.png           1400x560  marquee

then copies them to store-assets/screenshots/en/ and store-assets/promo/.
Every color comes from manifest.json. Copy is all-English. Re-runnable.
"""
import base64
import json
import os
import shutil
import colorsys
from pathlib import Path
from string import Template
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

MANIFEST = json.loads(Path("manifest.json").read_text(encoding="utf-8"))
MCOL = MANIFEST["theme"]["colors"]

REF = Path("store-assets/references")
SHOT = Path("store-assets/screenshots/en")
PROMO = Path("store-assets/promo")
for d in (REF, SHOT, PROMO):
    d.mkdir(parents=True, exist_ok=True)


# ---------- palette from manifest ----------
def rgb(c):
    return tuple(int(v) for v in c)


def hexs(c):
    return "#%02X%02X%02X" % rgb(c)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def tint(t):
    h, s, l = t
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (round(r * 255), round(g * 255), round(b * 255))


WHITE = (255, 255, 255)


def _lin(v):
    v /= 255.0
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def luminance(c):
    r, g, b = rgb(c)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def text_on(bg):
    """Pick ink or white for a card face, and require WCAG AA (4.5:1)."""
    ink = MCOL["tab_text"]
    ratio = contrast(ink, bg)
    if ratio >= contrast(WHITE, bg):
        assert ratio >= 4.5, f"contrast {ratio:.2f} too low on {hexs(bg)}"
        return ink
    assert contrast(WHITE, bg) >= 4.5, f"contrast too low on {hexs(bg)}"
    return WHITE


FRAME = rgb(MCOL["frame"])
FRAME_INACTIVE = rgb(MCOL["frame_inactive"])
FRAME_INC = rgb(MCOL["frame_incognito"])
TOOLBAR = rgb(MCOL["toolbar"])
TAB_BG = rgb(MCOL["background_tab"])
TAB_TEXT = rgb(MCOL["tab_text"])
TAB_TEXT_BG = rgb(MCOL["tab_background_text"])
TB_ICON = rgb(MCOL["toolbar_button_icon"])
BTN_BG = rgb(MCOL["button_background"])
OMNI_BG = rgb(MCOL["omnibox_background"])
OMNI_TEXT = rgb(MCOL["omnibox_text"])
BM_TEXT = rgb(MCOL["bookmark_text"])
NTP_BG = rgb(MCOL["ntp_background"])
NTP_TEXT = rgb(MCOL["ntp_text"])
NTP_LINK = rgb(MCOL["ntp_link"])
INK = mix(TAB_TEXT, WHITE, 0.35)  # neutral UI grey for Chrome-drawn page bits

PALETTE = {
    "FRAME": hexs(FRAME),
    "FRAME_INACTIVE": hexs(FRAME_INACTIVE),
    "FRAME_INC": hexs(FRAME_INC),
    "TOOLBAR": hexs(TOOLBAR),
    "TAB_BG": hexs(TAB_BG),
    "TAB_TEXT": hexs(TAB_TEXT),
    "TAB_TEXT_BG": hexs(TAB_TEXT_BG),
    "TB_ICON": hexs(TB_ICON),
    "BTN_BG": hexs(BTN_BG),
    "OMNI_BG": hexs(OMNI_BG),
    "OMNI_TEXT": hexs(OMNI_TEXT),
    "BM_TEXT": hexs(BM_TEXT),
    "NTP_BG": hexs(NTP_BG),
    "NTP_TEXT": hexs(NTP_TEXT),
    "NTP_LINK": hexs(NTP_LINK),
    "INK": hexs(INK),
}


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


# ---------- shared SVG icons (no unicode glyphs) ----------
IC_BACK = '<svg viewBox="0 0 16 16"><path d="M10 3.5 5.5 8l4.5 4.5"/></svg>'
IC_FWD = '<svg viewBox="0 0 16 16"><path d="M6 3.5 10.5 8 6 12.5"/></svg>'
IC_RELOAD = '<svg viewBox="0 0 16 16"><path d="M13 8a5 5 0 1 1-1.6-3.6"/><path d="M13.2 2.6v2.9h-2.9"/></svg>'
IC_DL = '<svg viewBox="0 0 16 16"><path d="M8 2.6v7.2"/><path d="M4.9 6.9 8 10 11.1 6.9"/><path d="M3 13.1h10"/></svg>'
IC_LENS = '<svg viewBox="0 0 16 16"><rect x="2.4" y="4.6" width="11.2" height="8.4" rx="2.2"/><circle cx="8" cy="8.8" r="2.3"/><path d="M6.1 4.6 7 3h2l.9 1.6"/></svg>'
IC_STAR = '<svg viewBox="0 0 16 16"><path d="M8 2.4 9.8 6.1l4 .6-2.9 2.8.7 4L8 11.6 4.4 13.5l.7-4L2.2 6.7l4-.6z"/></svg>'
IC_MORE = '<svg viewBox="0 0 16 16"><circle cx="8" cy="3.4" r="1.15" fill="currentColor" stroke="none"/><circle cx="8" cy="8" r="1.15" fill="currentColor" stroke="none"/><circle cx="8" cy="12.6" r="1.15" fill="currentColor" stroke="none"/></svg>'
IC_FOLDER = '<svg viewBox="0 0 16 16"><path d="M2.3 5a1.5 1.5 0 0 1 1.5-1.5h2.4l1.5 1.5h4.5A1.5 1.5 0 0 1 13.7 6.5v4.4a1.5 1.5 0 0 1-1.5 1.5H3.8a1.5 1.5 0 0 1-1.5-1.5z"/></svg>'
IC_SEARCH = '<svg viewBox="0 0 16 16" class="mag"><circle cx="7" cy="7" r="4.6"/><path d="m10.6 10.6 3.4 3.4"/></svg>'
IC_TUNE = '<svg viewBox="0 0 16 16"><path d="M3 5.5h10M3 10.5h10"/><circle cx="6" cy="5.5" r="1.8"/><circle cx="10.5" cy="10.5" r="1.8"/></svg>'
IC_MIC = ('<svg viewBox="0 0 16 16"><rect x="6.1" y="2.1" width="3.8" height="7.1" rx="1.9"/>'
          '<path d="M4.1 7.5a3.9 3.9 0 0 0 7.8 0"/><path d="M8 11.6v2.3"/><path d="M5.9 13.9h4.2"/></svg>')
# Google Lens mark: the real one is multicolour, so it is drawn in brand tones
# (sampled from the installed browser, not derived from the theme).
IC_LENS_C = ('<svg viewBox="0 0 16 16">'
             '<rect x="2.1" y="4.5" width="11.8" height="8.6" rx="2.3" fill="none" stroke="#4285F4" stroke-width="1.5"/>'
             '<path d="M6.1 4.5l.9-1.6h2l.9 1.6" fill="none" stroke="#EA4335" stroke-width="1.5"/>'
             '<circle cx="8" cy="8.7" r="2.2" fill="none" stroke="#34A853" stroke-width="1.5"/>'
             '<circle cx="11.5" cy="6.5" r="0.85" fill="#FBBC05" stroke="none"/></svg>')
IC_IMG = ('<svg viewBox="0 0 16 16"><rect x="2.1" y="3.4" width="11.8" height="9.2" rx="1.8"/>'
          '<circle cx="5.9" cy="6.5" r="1.1"/><path d="m3.4 11.7 3.3-3.1 2.3 2.1 1.8-1.5 2.7 2.5"/></svg>')
IC_GRID = ('<svg viewBox="0 0 16 16"><rect x="2.6" y="2.6" width="4.4" height="4.4" rx="1.1" stroke="none" fill="currentColor"/>'
           '<rect x="9" y="2.6" width="4.4" height="4.4" rx="1.1" stroke="none" fill="currentColor"/>'
           '<rect x="2.6" y="9" width="4.4" height="4.4" rx="1.1" stroke="none" fill="currentColor"/>'
           '<rect x="9" y="9" width="4.4" height="4.4" rx="1.1" stroke="none" fill="currentColor"/></svg>')

# new-tab shortcut tiles: (glyph, label, disc colour, glyph colour)
def _tile(path, label, disc, glyph):
    return (f'<div class="tile"><div class="disc" style="background:{disc};color:{glyph}">'
            f'<svg viewBox="0 0 24 24">{path}</svg></div><b>{label}</b></div>')


SHORTCUTS = [
    _tile('<path d="M8.6 6.4 16.8 12l-8.2 5.6z"/>', 'Videos', hexs(FRAME), '#FFFFFF'),
    _tile('<circle cx="12" cy="12" r="8.4"/>'
          '<path d="M3.6 12h16.8M12 3.6c2.3 2.4 3.5 5.3 3.5 8.4s-1.2 6-3.5 8.4'
          'c-2.3-2.4-3.5-5.3-3.5-8.4s1.2-6 3.5-8.4z"/>',
          'Web', hexs(FRAME_INC), '#FFFFFF'),
    _tile('<path d="M12 6.4v11.2M6.4 12h11.2"/>', 'Add shortcut', hexs(TAB_BG), hexs(TB_ICON)),
]

WINDOW_BTNS = (
    '<svg viewBox="0 0 12 12"><path d="M2.5 6.5h7"/></svg>',
    '<svg viewBox="0 0 12 12"><rect x="2.5" y="2.5" width="7" height="7"/></svg>',
    '<svg viewBox="0 0 12 12"><path d="M3 3l6 6M9 3l-6 6"/></svg>',
)

BOOKMARKS = ['Bookmarks', 'Reading', 'Design', 'Inspiration']
TAB_TITLES = [
    ('New Tab', True),
    ('Reading list', False),
]


def tab_svg(i):
    """Small favicon-ish glyph inside each tab."""
    shapes = [
        '<circle cx="8" cy="8" r="6"/>',
        '<rect x="2.5" y="2.5" width="11" height="11" rx="3"/>',
        '<path d="M8 2.2 13.8 13.8H2.2z"/>',
        '<path d="M2.5 12.5 8 3.5l5.5 9z"/>',
        '<rect x="2.5" y="4.5" width="11" height="7" rx="2"/>',
        '<circle cx="8" cy="8" r="5.4"/>',
    ]
    return f'<svg viewBox="0 0 16 16" class="fav-g">{shapes[i % len(shapes)]}</svg>'


# ---------- asset 1: full-window browser mockup ----------
BROWSER_HTML = Template("""<!doctype html>
<html><head><meta charset="utf-8"><style>
:root{
  --frame:$FRAME; --frame-inactive:$FRAME_INACTIVE; --frame-inc:$FRAME_INC;
  --toolbar:$TOOLBAR; --tab-bg:$TAB_BG; --tab-text:$TAB_TEXT; --tab-text-bg:$TAB_TEXT_BG;
  --tb-icon:$TB_ICON; --btn-bg:$BTN_BG; --omni-bg:$OMNI_BG; --omni-text:$OMNI_TEXT;
  --bm-text:$BM_TEXT; --ntp-bg:$NTP_BG; --ntp-text:$NTP_TEXT; --ntp-link:$NTP_LINK; --ink:$INK;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1280px;height:800px;overflow:hidden}
body{font-family:'Segoe UI',Arial,Helvetica,sans-serif;-webkit-font-smoothing:antialiased}
svg{fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.win{width:1280px;height:800px;display:flex;flex-direction:column}

/* tab strip = window frame */
.tabs{height:40px;background:var(--frame);display:flex;align-items:flex-end;padding-left:6px}
.tab{height:32px;display:flex;align-items:center;gap:8px;padding:0 10px;margin-right:2px;
     border-radius:10px 10px 0 0;font-size:12px;white-space:nowrap;max-width:196px}
.tab.active{background:var(--toolbar);color:var(--tab-text);font-weight:600}
.tab.idle{background:var(--frame);color:var(--tab-text-bg)}
.fav{width:15px;height:15px;flex:0 0 15px;display:flex;align-items:center;justify-content:center}
.fav-g{width:15px;height:15px;fill:currentColor;stroke:none;opacity:.85}
.tab.idle .fav-g{opacity:.7}
.x{width:13px;height:13px;flex:0 0 13px;opacity:.55;display:flex;align-items:center;justify-content:center}
.x svg{width:11px;height:11px;stroke-width:1.8}
.newtab{width:30px;height:30px;display:flex;align-items:center;justify-content:center;
        color:var(--tab-text-bg);opacity:.8;margin-bottom:2px}
.newtab svg{width:15px;height:15px;stroke-width:1.6}
.spacer{flex:1}
.win-btns{display:flex;align-items:center;height:40px;margin-bottom:0}
.win-btn{width:42px;height:36px;display:flex;align-items:center;justify-content:center;
         color:var(--tab-text);opacity:.55}
.win-btn svg{width:12px;height:12px}

/* toolbar */
.toolbar{height:44px;background:var(--toolbar);display:flex;align-items:center;gap:4px;padding:0 8px 0 10px}
.nav{width:30px;height:30px;display:flex;align-items:center;justify-content:center;
     color:var(--tb-icon);border-radius:15px}
.nav svg{width:17px;height:17px}
.omni{flex:1;height:30px;background:var(--omni-bg);border-radius:15px;
      display:flex;align-items:center;gap:9px;padding:0 13px;margin:0 10px;
      box-shadow:0 0 0 1px rgba(0,0,0,.11),0 1px 2px rgba(0,0,0,.05)}
.mag{width:15px;height:15px;color:var(--ink);flex:0 0 15px;opacity:.8}
.omni span{font-size:13px;color:var(--omni-text);opacity:.72;flex:1}
.right{display:flex;align-items:center;gap:12px}
.right svg{width:15px;height:15px}
.gblue{color:#1A73E8}
.tools{display:flex;align-items:center;gap:2px}
.tool{width:30px;height:30px;display:flex;align-items:center;justify-content:center;color:#5F6368}
.tool svg{width:16px;height:16px}

/* bookmark bar */
.bmbar{height:36px;background:var(--toolbar);display:flex;align-items:center;gap:22px;
       padding:0 14px;box-shadow:inset 0 -1px 0 rgba(0,0,0,.07)}
.bm{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--bm-text)}
.bm svg{width:14px;height:14px;color:var(--bm-text);opacity:.75}

/* new tab page */
.ntp{flex:1;background:var(--ntp-bg);position:relative;display:flex;
     flex-direction:column;align-items:center;padding-top:72px}
/* Chrome draws the alternate Google mark in one flat colour; tone sampled from the
   installed browser (#9AA0A6 soft grey on this ivory surface) - update here if it
   renders differently and re-run, never patch the PNG. */
.glogo{font-size:76px;font-weight:600;letter-spacing:-1.5px;color:#9AA0A6;
       font-family:'Segoe UI',Arial,sans-serif;line-height:1}
.search{margin-top:24px;width:584px;height:54px;background:#FFFFFF;border-radius:27px;
        display:flex;align-items:center;gap:13px;padding:0 20px;
        box-shadow:0 0 0 1px rgba(0,0,0,.05),0 1px 6px rgba(32,33,36,.16)}
.search .mag{width:18px;height:18px;opacity:.75}
.search span{font-size:16px;color:var(--ink);opacity:.78;flex:1}
.search .right{gap:14px}
.search .right svg{width:18px;height:18px}
.search .right .mic{color:#5F6368}
.ntp-top{position:absolute;right:22px;top:14px;display:flex;align-items:center;gap:20px;
         color:#5F6368}
.ntp-act{display:flex;align-items:center;gap:7px;font-size:12.5px;opacity:.92}
.ntp-act svg{width:15px;height:15px;stroke-width:1.5}
.tiles{margin-top:28px;display:flex;gap:36px}
.tile{display:flex;flex-direction:column;align-items:center;width:76px}
.tile .disc{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;
            justify-content:center;box-shadow:0 1px 3px rgba(32,33,36,.14)}
.tile .disc svg{width:22px;height:22px;stroke-width:1.7}
.tile b{font-size:11.5px;font-weight:400;color:var(--ink);margin-top:10px;opacity:.88}
.customize{position:absolute;right:24px;bottom:20px;height:32px;padding:0 15px;border-radius:16px;
           background:#202124;color:#FFFFFF;display:flex;align-items:center;gap:8px;font-size:12px}
.customize svg{width:14px;height:14px}
</style></head><body>
<div class="win">
  <div class="tabs">
    $TABS
    <div class="newtab"><svg viewBox="0 0 16 16"><path d="M8 3.5v9M3.5 8h9"/></svg></div>
    <div class="spacer"></div>
    <div class="win-btns">$WINBTNS</div>
  </div>
  <div class="toolbar">
    <div class="nav">$IC_BACK</div>
    <div class="nav">$IC_FWD</div>
    <div class="nav">$IC_RELOAD</div>
    <div class="omni">$IC_SEARCH<span>Search or type a URL</span>
      <div class="right"><span class="gblue">$IC_DL</span><span class="gblue">$IC_LENS</span></div>
    </div>
    <div class="tools"><div class="tool">$IC_STAR</div><div class="tool">$IC_MORE</div></div>
  </div>
  <div class="bmbar">$BOOKMARKS</div>
  <div class="ntp">
    <div class="ntp-top">
      <div class="ntp-act">$IC_IMG<span>Images</span></div>
      <div class="ntp-act">$IC_GRID<span>Apps</span></div>
    </div>
    <div class="glogo">Google</div>
    <div class="search">$IC_SEARCH<span>Search Google or type a URL</span>
      <div class="right"><span class="mic">$IC_MIC</span><span>$IC_LENS_C</span></div>
    </div>
    <div class="tiles">$TILES</div>
    <div class="customize">$IC_TUNE<span>Customize Chrome</span></div>
  </div>
</div>
</body></html>""")


X_BTN = '<div class="x"><svg viewBox="0 0 16 16"><path d="M4 4l8 8M12 4l-8 8"/></svg></div>'


def html_browser():
    tabs = []
    for i, (title, active) in enumerate(TAB_TITLES):
        cls = "active" if active else "idle"
        tabs.append(f'<div class="tab {cls}"><span class="fav">{tab_svg(i)}</span>'
                    f'<span class="title">{title}</span>{X_BTN}</div>')
    bookmarks = "".join(f'<div class="bm">{IC_FOLDER}<span>{b}</span></div>' for b in BOOKMARKS)
    winbtns = "".join(f'<div class="win-btn">{b}</div>' for b in WINDOW_BTNS)
    tiles = "".join(SHORTCUTS)
    sub = dict(PALETTE)
    sub.update(TABS="".join(tabs), BOOKMARKS=bookmarks, WINBTNS=winbtns, TILES=tiles,
               IC_BACK=IC_BACK, IC_FWD=IC_FWD, IC_RELOAD=IC_RELOAD, IC_SEARCH=IC_SEARCH,
               IC_DL=IC_DL, IC_LENS=IC_LENS, IC_STAR=IC_STAR, IC_MORE=IC_MORE,
               IC_FOLDER=IC_FOLDER, IC_TUNE=IC_TUNE, IC_MIC=IC_MIC,
               IC_LENS_C=IC_LENS_C, IC_IMG=IC_IMG, IC_GRID=IC_GRID)
    return BROWSER_HTML.substitute(sub)


# ---------- asset 2: intro + color cards ----------
INTRO_HTML = Template("""<!doctype html>
<html><head><meta charset="utf-8"><style>
:root{--frame:$FRAME;--toolbar:$TOOLBAR;--ntp-bg:$NTP_BG;--ntp-text:$NTP_TEXT;
      --ntp-link:$NTP_LINK;--frame-inc:$FRAME_INC;--tab-text:$TAB_TEXT}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1280px;height:800px;overflow:hidden}
body{font-family:'Segoe UI',Arial,Helvetica,sans-serif;background:var(--ntp-bg)}
.wrap{padding:82px 96px 0;display:flex;flex-direction:column;height:800px}
.head{display:flex;align-items:center;gap:30px}
.head img{width:104px;height:104px;border-radius:24px;box-shadow:0 10px 30px rgba(60,50,110,.18)}
.kicker{font-size:13px;letter-spacing:4px;color:var(--ntp-link);font-weight:600}
h1{font-family:Georgia,'Times New Roman',serif;font-size:56px;font-weight:400;
   color:var(--ntp-text);margin-top:12px;line-height:1.05}
.tag{margin-top:14px;font-size:19px;color:$BM_TEXT}
.cards{margin-top:56px;display:grid;grid-template-columns:1fr 1fr;gap:26px}
.card{height:150px;border-radius:20px;padding:26px 28px;display:flex;flex-direction:column;justify-content:center}
.card b{font-size:27px;font-weight:600;letter-spacing:.2px}
.card span{margin-top:9px;font-size:15px;opacity:.82}
.chips{margin-top:auto;margin-bottom:56px;display:flex;gap:12px}
.chip{padding:9px 18px;border-radius:999px;font-size:13.5px;color:var(--ntp-text);
      box-shadow:inset 0 0 0 1px rgba(33,32,44,.16)}
.rule{height:1px;background:rgba(33,32,44,.12);margin-top:44px}
</style></head><body>
<div class="wrap">
  <div class="head">
    <img src="$LOGO">
    <div>
      <div class="kicker">A LITTLE TIDAL CALM</div>
      <h1>Chill Wave</h1>
      <div class="tag">Soft violet tides for a quieter browser.</div>
    </div>
  </div>
  <div class="cards">$CARDS</div>
  <div class="rule"></div>
  <div class="chips">
    <div class="chip">Solid colors</div>
    <div class="chip">No wallpaper</div>
    <div class="chip">Soft contrast</div>
    <div class="chip">Distraction-free</div>
  </div>
</div>
</body></html>""")


def html_intro():
    faces = [
        ("Frame", FRAME, "#A09BD9 · Window frame & tab strip", "Tab strip, window frame"),
        ("Toolbar", TOOLBAR, "#F3F2F5 · Toolbar & bookmark bar", "Toolbar, bookmarks"),
        ("New Tab", NTP_BG, "#F8F8F9 · New tab surface", "New tab background"),
        ("Ink", TAB_TEXT, "#262532 · Titles & text", "Tab titles, address bar"),
    ]
    cards = ""
    for name, bg, spec, _use in faces:
        fg = text_on(bg)
        edge = "" if fg is WHITE else "box-shadow:inset 0 0 0 1px rgba(33,32,44,.16);"
        cards += (f'<div class="card" style="background:{hexs(bg)};color:{hexs(fg)};{edge}">'
                  f'<b>{name}</b><span>{spec}</span></div>')
    return INTRO_HTML.substitute(dict(PALETTE, LOGO=data_uri("logo/logo.png"), CARDS=cards))


# ---------- asset 3: promo 440x280 ----------
PROMO_TILE_HTML = Template("""<!doctype html>
<html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:440px;height:280px;overflow:hidden}
body{background:$DEEP;display:flex;flex-direction:column;align-items:center;
     font-family:'Segoe UI',Arial,Helvetica,sans-serif;position:relative}
.card{width:112px;height:112px;background:#FFFFFF;border-radius:26px;margin-top:26px;
      display:flex;align-items:center;justify-content:center;
      box-shadow:0 12px 30px rgba(10,14,40,.30)}
.card img{width:88px;height:88px}
h1{font-family:Georgia,'Times New Roman',serif;font-size:31px;font-weight:400;color:#FFFFFF;margin-top:20px}
.kicker{font-size:11px;letter-spacing:3.4px;color:rgba(255,255,255,.82);margin-top:11px}
.tag{font-size:12.5px;color:rgba(255,255,255,.88);margin-top:10px}
.bar{position:absolute;left:0;right:0;bottom:0;height:14px;background:$BAR}
</style></head><body>
  <div class="card"><img src="$LOGO"></div>
  <h1>Chill Wave</h1>
  <div class="kicker">CHROME THEME</div>
  <div class="tag">Soft violet tides for a quieter browser.</div>
  <div class="bar"></div>
</body></html>""")


def html_promo_tile():
    return PROMO_TILE_HTML.substitute(LOGO=data_uri("logo/logo.png"),
                                       DEEP=hexs(NTP_LINK), BAR=hexs(TOOLBAR))


# ---------- asset 4: promo 1400x560 ----------
PROMO_MARQUEE_HTML = Template("""<!doctype html>
<html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1400px;height:560px;overflow:hidden}
body{background:$BG;display:flex;flex-direction:column;align-items:center;
     font-family:'Segoe UI',Arial,Helvetica,sans-serif;position:relative}
.top{position:absolute;left:0;right:0;top:0;height:8px;background:$ACCENT}
h1{font-family:Georgia,'Times New Roman',serif;font-size:46px;font-weight:400;
   color:$TEXT;margin-top:46px}
.tag{font-size:19px;color:$SUB;margin-top:12px}
.shot{margin-top:24px;width:580px;border-radius:12px;overflow:hidden;
      box-shadow:0 0 0 2px $ACCENT,0 22px 50px rgba(60,50,110,.22)}
.shot img{display:block;width:580px}
</style></head><body>
  <div class="top"></div>
  <h1>Chill Wave</h1>
  <div class="tag">Soft violet tides for a quieter browser.</div>
  <div class="shot"><img src="$SHOT"></div>
</body></html>""")


def html_promo_marquee(shot_png):
    return PROMO_MARQUEE_HTML.substitute(SHOT=data_uri(shot_png), BG=hexs(NTP_BG),
                                         ACCENT=hexs(FRAME), TEXT=hexs(NTP_TEXT),
                                         SUB=hexs(BM_TEXT))


# ---------- render ----------
def render(pw, html, w, h, out):
    page = pw.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    page.set_content(html, wait_until="load")
    page.wait_for_timeout(120)
    page.screenshot(path=str(out))
    page.close()
    im = Image.open(out).convert("RGB")
    assert im.size == (w, h), f"{out} is {im.size}, expected {(w, h)}"
    im.save(out)
    return out


def main():
    assert MANIFEST["theme"]["properties"]["ntp_logo_alternate"] == 1, \
        "this mockup assumes ntp_logo_alternate=1 (single-colour Google mark)"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        try:
            render(b, html_browser(), 1280, 800, REF / "screenshot-1-browser.png")
            render(b, html_intro(), 1280, 800, REF / "screenshot-2-introduction.png")
            render(b, html_promo_tile(), 440, 280, REF / "promo-440x280.png")
            render(b, html_promo_marquee(REF / "screenshot-1-browser.png"), 1400, 560,
                   REF / "promo-1400x560.png")
        finally:
            b.close()
    for name in ("screenshot-1-browser.png", "screenshot-2-introduction.png"):
        shutil.copy(REF / name, SHOT / name)
    shutil.copy(REF / "promo-440x280.png", PROMO / "440x280.png")
    shutil.copy(REF / "promo-1400x560.png", PROMO / "1400x560.png")
    print("done -> 4 store assets (2 screenshots + 2 promo)")


if __name__ == "__main__":
    main()