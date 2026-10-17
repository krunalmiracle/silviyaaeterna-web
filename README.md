# Silviya Aeterna

A bilingual English/Bulgarian personal site for practical skincare, everyday wellbeing, family conversations and mental-health reflection. Light default, cool silver accents and six original daylight scenes. Live at https://silviyaaeterna.krusil.com/.

No clinical or commercial endorsement is implied. The two shopping destinations lead to official Oriflame Bulgaria; a Silviya-specific referral link has not been provided. The future YouTube destination is clearly marked as coming soon.

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

The six original generated PNGs and generation manifest are archived at `/opt/data/home/silviyaaeterna-daylight-source/` (development only). The delivered source images are optimized WebPs with 780px responsive variants. `tools/ASSET-MANIFEST.json` lists the exact source and derivative hashes, prompts, dimensions and bilingual alt text. `assets/social-og.png` is derived from the new conservatory image, not the retired garden art. See `tools/ASSET-PROVENANCE.md`. No original PNGs or developer notes are published by the static server.

The old moonlit/gold design documents and art generation helpers are historical artifacts only. `PRODUCT.md` and `DESIGN.md` describe the current site. Self-hosted fonts and GSAP remain licensed with their files.
