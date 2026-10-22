# Silviya Aeterna

A bilingual English/Bulgarian Oriflame product-discovery and joining site. Eight verified Bulgarian listings with official product images, dated EUR prices and exact product links lead the page; four practical lifestyle themes follow. Light default, cool silver accents and six original daylight editorial scenes. Live at https://silviyaaeterna.krusil.com/.

No clinical endorsement, guaranteed earnings or personal referral attribution is implied. The VIP and partner forms are official but generic. Silviya's invitation code/link has not been provided; obtain it before registration if attribution to her matters. The partner route lists the official €10 annual fee, added to the first order. The future YouTube destination is marked coming soon.

## Run and test

Node 22+ or Bun:

    npm start
    npm test

The static Bun server keeps security headers and serves only `index.html` and `assets/`. No database, auth, forms, secrets, analytics or third-party runtime resources. Docker listens on port 3000 behind Dokploy.

## Browser acceptance

    python3 -m pip install --target /opt/data/cache/scratch/aeterna-py patchright
    PYTHONPATH=/opt/data/cache/scratch/aeterna-py python3 tools/shots.py

The isolated dependency target can be recreated if scratch storage is pruned.

The script opens an isolated local Chromium, checks both languages at 1440, 1024, 768, 390 and 320px, and closes browser/server when done. See its freshly generated report for current results; previous `.impeccable` screenshots and reports may describe the retired appearance and must not be used as current evidence.

## Images and provenance

The six original generated PNGs and generation manifest are archived at `/opt/data/home/silviyaaeterna-daylight-source/` (development only). The delivered editorial images are optimized WebPs with 780px responsive variants. `tools/ASSET-MANIFEST.json` lists their source and derivative hashes, prompts, dimensions and bilingual alt text. Eight official product images are locally optimized into `assets/products/`; `tools/ORIFLAME-PRODUCTS.json` preserves their exact source URLs, source and derivative hashes, product codes, dated stock and EUR price evidence. The source HTML and original product-image bytes are archived at `/opt/data/home/silviyaaeterna-oriflame-sources/2026-10-22/`, outside the served allowlist. `assets/social-og.png` derives from the conservatory image. No source originals or developer notes are published by the static server.

The old moonlit/gold design documents and art generation helpers are historical artifacts only. `PRODUCT.md` and `DESIGN.md` describe the current site. Self-hosted fonts and GSAP remain licensed with their files.
