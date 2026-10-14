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

Evidence: .impeccable/review/report.json, EN/BG desktop/mobile full and viewport PNGs, mobile-menu-en.png/mobile-menu-bg.png and mobile-reflection-en.png/mobile-reflection-bg.png. Final verification: 32/32 tests, 284/284 browser checks, no request/console errors, zero overflow at all ten language/viewport combinations. The pre-integration layout-only evidence was removed after full acceptance; the script's --layout-only option is diagnostic only, never image acceptance.

## Original images

The independent asset producer supplies hero-glasshouse.webp, sky-study.webp, skin-ritual.webp, quiet-growth.webp, ASSET-MANIFEST.json and SUMMARY.md. Integrate only after all originals exist:

    uv run --with pillow python tools/prepare_images.py /opt/data/home/silviya-glasshouse-assets

This copies four hash-verified WebPs, creates a mobile hero derivative and a real 1200x630 PNG social card from the original hero and Onest lettering. Producer metadata is retained intact under tools/. Actual dimensions and EN/BG descriptions match the manifest and are regression-tested. Final renderer: Mitsuba CPU from Blender-authored geometry. No image-model, photographic or stock-source claims are made. See tools/glasshouse-source/README.md for the exact small-source snapshot layout and external complete-source archive; reproduction requires restoring or rebuilding excluded geometry first.

Onest source: https://github.com/google/fonts/tree/main/ofl/onest, SIL Open Font License 1.1; source TTF and conversion script under tools/, WOFF2 and license under assets/fonts/. Geist is the existing Cyrillic-capable self-hosted subset, also OFL.

    uv run --with fonttools --with brotli python tools/prepare_font.py

Read-only image/font/evidence verification, writing a development report:

    uv run --with pillow --with fonttools --with brotli python tools/verify_delivery.py

## Development-only documentation

PRODUCT.md records facts and visual constraints; DESIGN.md and .impeccable/design.json describe the built system; .impeccable/surfaces/index-html.md carries the approved direction contract. tools/ carries provenance and generator code. None are served by the static server.

## Release boundary

Implementation worker may commit locally on the named worktree branch only. Local implementation and builder verification are complete. Parent owns independent review, merge, push and Dokploy release; builder verification is not an independent judge pass or a production deployment.

Public canonical and social metadata use https://silviyaaeterna.krusil.com/ and the absolute /assets/social-og.png URL. No channel/shop destination exists; #channel and #shop are explicitly coming soon. Future links require confirmed destinations and bilingual labels.
