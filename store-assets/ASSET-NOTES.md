# Store artwork notes — Chill Wave Theme

All four store assets are rendered from one HTML/CSS source by
`scripts/generate-store-assets.py` (headless Chromium via Playwright,
`device_scale_factor=1`). Nothing is patched on top of an older PNG: edit the
composer, then re-run the script to regenerate the full set.

```
python3 scripts/generate-logo.py          # -> logo/logo.png (128x128)
python3 scripts/generate-store-assets.py  # -> 2 screenshots + 2 promo tiles
```

## Files

| Asset | Size | Path |
|-------|------|------|
| Full-window mockup | 1280×800 | `store-assets/screenshots/en/screenshot-1-browser.png` |
| Intro + colour cards | 1280×800 | `store-assets/screenshots/en/screenshot-2-introduction.png` |
| Brand tile | 440×280 | `store-assets/promo/440x280.png` |
| Marquee | 1400×560 | `store-assets/promo/1400x560.png` |

Intermediate HTML + PNG stay in `store-assets/references/` and are committed so
the composition can be reviewed as source, not only as a flat image.

## Colour sourcing

Every colour is read from `manifest.json` at render time (`theme.colors`), so
the artwork can never drift from the shipped palette. No colour literals live in
the HTML. The two derived greys are computed in the script:

- `INK` — neutral UI grey for the parts Chrome draws itself (new-tab search
  field, shortcut tiles, the Google mark).
- Card label colour — picked by WCAG contrast: `text_on()` returns ink or white
  for a given face and **asserts the ratio is at least 4.5:1**.

The colour cards on `screenshot-2` are printed with their hex values, and the
two near-white faces (`#F3F2F5`, `#F8F8F9`) carry a 1px inset border so they do
not dissolve into the page background.

## Chrome-drawn UI (calibration notes)

- **Google mark on the new-tab page.** The manifest sets
  `properties.ntp_logo_alternate: 1`, so Chrome paints the mark in one flat
  colour instead of the brand colours. The mockup paints it in the theme link
  colour (Tide Blue), the tone a light new-tab surface resolves to. If the
  installed browser renders a different tone, change the `.glogo` colour in
  `scripts/generate-store-assets.py` and re-run — do not hand-edit the PNG.
- **Shortcut tiles** are page content, not theme surfaces; the mockup draws three
  of them (two in theme violet, one neutral "Add shortcut") the way Chrome lays
  them out on a fresh profile.
- **Toolbar and omnibox glyphs** (star, ⋮, download, Lens) use Chrome's own UI
  colours, matched to the real browser rather than derived from the theme.
- **Customize Chrome pill** is drawn by Chrome itself and keeps its own dark
  surface (`#202124`) with white text.
- **Window buttons** keep the light tab-text tone against the lilac frame.
- **Tab strip** uses the frame colour; the active tab uses the toolbar colour so
  it merges into the toolbar the way Chrome draws it.

## Icon

`logo/logo.png` is drawn by `scripts/generate-logo.py` — a crescent moon, three
stars and two soft tide layers over a night-blue → violet gradient, supersampled
6× and masked to a 22.5% corner radius. The four explored alternatives (and the
comparison sheet) are kept in `store-assets/icon-candidates/`.