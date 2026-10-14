# Silviya Aeterna

Daylight Glasshouse: a bilingual EN/BG personal project covering astrology, numerology, skincare, psychology-informed wellbeing, family/children and mental health.

Static HTML/CSS/small JavaScript, self-hosted fonts and original local raster art. No backend features, forms, tracking, cookies, secrets or third-party runtime requests. The existing hardened server and Bun Docker port 3000 remain unchanged.

## Local development

Node 22+ or Bun:

    npm start
    npm test

HOST defaults to 0.0.0.0, PORT to 3000. Tests start their own bounded localhost server on port 43117.

## Browser acceptance

    uv run --with patchright python tools/shots.py

Uses an installed local Chromium, creates an isolated temporary profile, starts its own localhost server on 43118, and closes browser/server on completion or failure. It never opens a login profile. Tests both languages at 1440, 390, 320, 768 and 1024px. Covers decoded images, overflow, touch targets, keyboard entry, theme selection, sticky headroom, language persistence, denied storage, reduced motion, mobile menu and no-JavaScript behavior.

Evidence: .impeccable/review/report.json, EN/BG desktop/mobile full and viewport PNGs, and mobile-menu-en.png/mobile-menu-bg.png. The --layout-only option intentionally performs no image acceptance or screenshots and records missing asset requests in layout-only.json. That is not a passing delivery review.

## Original images

The independent asset producer supplies hero-glasshouse.webp, sky-study.webp, skin-ritual.webp, quiet-growth.webp, ASSET-MANIFEST.json and SUMMARY.md. Integrate only after all originals exist:

    uv run --with pillow python tools/prepare_images.py /opt/data/home/silviya-glasshouse-assets

This copies four verified WebPs, creates a mobile hero derivative and a real 1200x630 PNG social card from the original hero and Onest lettering. Producer metadata is retained intact under tools/. Confirm actual dimensions and image descriptions against the HTML before final screenshots. No image-model, photographic or stock-source claims are made.

Onest source: https://github.com/google/fonts/tree/main/ofl/onest, SIL Open Font License 1.1; source TTF and conversion script under tools/, WOFF2 and license under assets/fonts/. Geist is the existing Cyrillic-capable self-hosted subset, also OFL.

    uv run --with fonttools --with brotli python tools/prepare_font.py

## Development-only documentation

PRODUCT.md records facts and visual constraints; DESIGN.md and .impeccable/design.json describe the built system; .impeccable/surfaces/index-html.md carries the approved direction contract. tools/ carries provenance and generator code. None are served by the static server.

## Release boundary

Implementation worker may commit locally on the named worktree branch only. Parent owns independent review, merge, push and Dokploy release. This checkout must not be deployed while image input or final acceptance is pending.

Public canonical and social metadata use https://silviyaaeterna.krusil.com/ and the absolute /assets/social-og.png URL. No channel/shop destination exists; #channel and #shop are explicitly coming soon. Future links require confirmed destinations and bilingual labels.
