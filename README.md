<div align="center">
  <img src="https://raw.githubusercontent.com/vaxicy/chill-wave-theme/main/logo/logo.png" alt="Chill Wave Theme icon" width="88">
  <h1>Chill Wave Theme</h1>
  <p>A calm violet Chrome theme with soft lilac surfaces, near-white reading areas and one deep-blue accent.</p>
  <p>
    <img src="https://img.shields.io/badge/version-1.0.0-A09BD9" alt="Version 1.0.0">
    <img src="https://img.shields.io/badge/license-Non--Commercial-lightgrey" alt="Non-Commercial License">
    <img src="https://img.shields.io/badge/Chrome%20Web%20Store-theme-A09BD9?logo=googlechrome" alt="Chrome Web Store">
  </p>
</div>

---

## About

Chill Wave washes the browser in soft violet tides. A lilac frame carries the window and the tab strip, an almost-white toolbar and bookmark bar sit just below it, and the new tab page opens on a near-white surface where a single deep-blue accent marks links and headings.

Every layer is painted as one flat solid colour, so nothing competes for attention while you read, write or plan. Text tones are tuned so tab titles, toolbar icons, bookmarks and the address bar stay legible against the light surfaces, and incognito windows keep a slightly deeper violet frame so private windows stay visually distinct.

## Preview

*The full window: lilac frame, mist toolbar and the ivory new tab page.*

![Chill Wave Theme browser preview](https://raw.githubusercontent.com/vaxicy/chill-wave-theme/main/store-assets/screenshots/en/screenshot-1-browser.png)

*The four colours the theme is built from.*

![Chill Wave Theme colour palette](https://raw.githubusercontent.com/vaxicy/chill-wave-theme/main/store-assets/screenshots/en/screenshot-2-introduction.png)

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Window Lilac | `#A09BD9` | Window frame, tab strip, window buttons |
| Soft Lavender | `#CBC8DA` | Inactive window frame |
| Toolbar Mist | `#F3F2F5` | Toolbar, bookmark bar, active tab |
| Idle Tab | `#D5D5E4` | Background tabs |
| Address Bar White | `#FEFEFE` | Omnibox surface |
| New Tab Ivory | `#F8F8F9` | New tab page background |
| Tide Blue | `#4B5E96` | Links, new-tab headings, store artwork accent |
| Midnight Ink | `#262532` | Tab titles, address bar text |
| Muted Ink | `#444255` | Inactive tab titles |
| Toolbar Grey | `#59576F` | Toolbar icons, bookmark text |
| Incognito Violet | `#8B85D1` | Incognito window frame |

## Chrome UI Notes

Some parts of the browser are painted by Chrome itself rather than by the theme manifest. The store artwork follows what Chrome renders after installing this theme:

- **Google mark on the new-tab page:** the manifest sets `ntp_logo_alternate: 1`, so Chrome draws it as one flat colour instead of the brand colours — on this ivory surface it resolves to the theme's Tide Blue.
- **Shortcut tiles:** the round new-tab shortcuts are page content, drawn here in theme violet with a neutral "Add shortcut" tile.
- **Chrome's own UI:** the star, the ⋮ menu, the download / Lens icons in the address bar and the Customize Chrome pill keep Chrome's own tones rather than the theme's.
- **Window buttons:** minimize / maximize / close stay in the light tab-text tone against the lilac frame.
- **Address bar:** the omnibox keeps its own near-white surface, so it reads slightly brighter than the toolbar around it.

## Features

| Feature | Detail |
|---------|--------|
| 🌊 Violet tide palette | Lilac frame over an ivory reading surface |
| 🌙 Moon-tide icon | Crescent moon and two soft tide layers, drawn in code |
| 🎨 Flat colour layers | Every surface is one solid colour, no wallpaper |
| 👓 Tuned contrast | Tabs, toolbar, bookmarks and address bar stay legible |
| 🕶️ Incognito styling | A deeper violet frame keeps private windows distinct |
| 🪶 Pure theme package | A manifest and an icon, nothing else to install |

## Install

### From source (unpacked)

1. Download or clone this repository.
2. Open Chrome and navigate to `chrome://extensions`.
3. Enable **Developer mode** in the top-right corner.
4. Click **Load unpacked** and select this folder.

### From Chrome Web Store

Search for **Chill Wave Theme** in the Chrome Web Store and install it.

## Files

| File | Description |
|------|-------------|
| `manifest.json` | Chrome theme manifest (MV3) with inline `theme` config |
| `logo/logo.png` | Theme icon (128×128) |
| `store-assets/screenshots/en/` | Store listing screenshots (1280×800) |
| `store-assets/promo/` | Promo tiles (440×280 and 1400×560) |
| `store-assets/store-description.txt` | Store listing description (English) |
| `store-assets/ASSET-NOTES.md` | How the store artwork is composed and calibrated |
| `store-assets/icon-candidates/` | The explored logo concepts and their comparison sheet |
| `store-assets/references/` | Intermediate HTML + PNG used by the composer |
| `scripts/generate-logo.py` | Draws `logo/logo.png` |
| `scripts/generate-store-assets.py` | Renders every store asset from one HTML/CSS source |
| `scripts/generate_logo_candidates.py` | Draws the four explored logo concepts |
| `scripts/package.py` | Builds the release ZIP into the default output folder |

## Packaging

```bash
python3 scripts/package.py
```

The archive is written as `chill-wave-theme-<version>.zip` into the default output folder two levels above this project (`...\vibe coding\`). The version stays `1.0.0` for the first store upload.

Packaged: `manifest.json`, `README.md`, `LICENSE`, `logo/`. Left out, because the Chrome Web Store takes them as separate uploads: `store-assets/` (screenshots, promo tiles, listing text), `scripts/`, `.gitignore`. The script re-reads `manifest.json` from inside the finished archive and fails if the archive root or the referenced files are wrong.

## License

Non-Commercial License — personal use permitted.

- ✅ Personal use, modification for personal use, sharing with attribution.
- ❌ Commercial use — a commercial licence is required.

For commercial licensing, contact the author. See [LICENSE](LICENSE) for the full text.