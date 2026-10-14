# Asset provenance and pending input

## Status

No original still-life WebPs have been integrated yet. tools/prepare_images.py refused integration because all four final images and the producer manifest/summary were absent. Do not treat the page as visually complete or deploy it.

Expected producer inputs: /opt/data/home/silviya-glasshouse-assets/{hero-glasshouse.webp,sky-study.webp,skin-ritual.webp,quiet-growth.webp,ASSET-MANIFEST.json,SUMMARY.md}.

The producer manifest will be authoritative about the rendering method, dimensions, output hashes and source. The page is intended to use original local 3D still-life illustrations, not AI photographs or real products/locations. The pending image descriptions and intrinsic dimensions in index.html must be checked against delivered artwork before final acceptance.

The former orbit-chart SVG imagery, old social PNG and stale screenshots have been removed, rather than being passed off as the replacement.

## Existing font assets

Onest variable TTF downloaded from https://raw.githubusercontent.com/google/fonts/main/ofl/onest/Onest%5Bwght%5D.ttf. License fetched from the same directory's OFL.txt; retained as assets/fonts/Onest-OFL.txt. Source SHA-256: 966c5c29b4755da84b6854d5c21dd4eaa2420225d0e9874de602de176d4a9f31.

Source retained under tools/Onest-source.ttf, converted by tools/prepare_font.py using fontTools and Brotli into the self-hosted assets/fonts/Onest-Variable.woff2. All 49 Cyrillic codepoints used by the current page were verified against the source cmap. No font CDN is used at runtime.

Geist-Variable-subset.woff2 and OFL-1.1.txt are inherited local assets from the previous version. The source is the existing committed project asset, not a newly claimed download.

## Authored UI mark

assets/favicon.svg is locally authored vector code: an outlined leaf and restrained amber circle on jade. It is a small identity mark only; not a substitute for the original raster illustrations.

## Planned derived files

When originals arrive, tools/prepare_images.py copies exact source WebPs, retains the manifest under tools/, creates a 780px-wide mobile derivative with source metadata, and composites a 1200x630 PNG social preview from the actual hero plus real Onest brand text. This note must be updated with verified integration evidence after that script succeeds. Generator scripts, source files and manifests remain unserved under tools/.
