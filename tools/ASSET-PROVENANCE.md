# Asset provenance: integrated original glasshouse renders

## Status

All four final original WebPs are integrated, decoded and visually inspected. tools/prepare_images.py validated exact dimensions, byte counts, embedded XMP and SHA-256 values against the delivered manifest before copying. The npm regression suite also checks unchanged original hashes, HTML dimensions and exact EN/BG alt text. Builder verification is complete; independent judge and release belong to the parent.

Producer origin: /opt/data/home/silviya-glasshouse-assets/. Unchanged manifest: tools/ASSET-MANIFEST.json. Producer execution record: tools/ASSET-SUMMARY.md. Integrated output inventory: tools/INTEGRATED-ASSETS.json. Final decoded asset/font/screenshot hashes: .impeccable/review/verification.json.

Actual method: original procedural geometry authored with Blender 5.2.2, exported as PLY by export_scenes.py, then rendered using Mitsuba 3.9.1 LLVM CPU at 64 samples with bounded tiles and three threads. Mild OpenCV non-local-means denoising is non-generative cleanup. Final images are not Cycles output: the producer's two Cycles attempts failed before producing any final image. No image model, stock, photographs, external textures, real products or real location claims are used.

Original files, copied byte-for-byte with embedded XMP:

- assets/images/hero-glasshouse.webp: 1800x1200, 188588 bytes. Amber sphere, foliage, mineral plinth and shallow water dish.
- assets/images/sky-study.webp: 1400x1050, 103304 bytes. Mineral sphere and amber crescent with a botanical branch.
- assets/images/skin-ritual.webp: 1400x1050, 92392 bytes. Unlabelled frosted vessel, porcelain water bowl and broad green leaves.
- assets/images/quiet-growth.webp: 1400x1050, 116522 bytes. Ribbed spruce vase, leafy branches and nested pale/amber bowls.

Complete source remains in the original producer directory, including editable .blend scenes, meshes, PNG originals and render records. The website retains the eight requested small source/dependency/origin files under tools/glasshouse-source/source/, plus WebP sidecars and the producer summary. Its README explains the asset-root/source layout and the need to restore or regenerate excluded geometry before reproduction. Do not run render.py's unsuccessful Cycles entrypoint as if it were the final renderer. The saved render_mitsuba.py hash matches every manifest entry.

The former orbit-chart SVG imagery and old social PNG were removed. Current screenshots show this complete raster-led replacement, not the prior site.

## Existing font assets

Onest variable TTF downloaded from https://raw.githubusercontent.com/google/fonts/main/ofl/onest/Onest%5Bwght%5D.ttf. License fetched from the same directory's OFL.txt; retained as assets/fonts/Onest-OFL.txt. Source SHA-256: 966c5c29b4755da84b6854d5c21dd4eaa2420225d0e9874de602de176d4a9f31.

Source retained under tools/Onest-source.ttf, converted by tools/prepare_font.py using fontTools and Brotli into the self-hosted assets/fonts/Onest-Variable.woff2. All 49 Cyrillic codepoints used by the current page were verified against the source cmap. No font CDN is used at runtime.

Geist-Variable-subset.woff2 and OFL-1.1.txt are inherited local assets from the previous version. The source is the existing committed project asset, not a newly claimed download. tools/verify_delivery.py checked all 49 used Cyrillic codepoints against both final shipping WOFF2 files, with no missing glyphs; the EN/BG screenshots were also read visually.

## Authored UI mark

assets/favicon.svg is locally authored vector code: an outlined leaf and restrained amber circle on jade. It is a small identity mark only; not a substitute for the original raster illustrations.

## Verified derived files

assets/images/hero-glasshouse-mobile.webp is a 780x520 Pillow derivative of the actual hero (26552 bytes), with embedded XMP identifying the original render. It preserves the whole source composition; the mobile CSS crop is 55% 50%, retaining the sphere and foliage.

assets/social-og.png is a genuine 1200x630 PNG (375390 bytes), composited with Pillow from the original hero and Onest brand lettering. PNG text records its source and derivative method. It was decoded and visually inspected; canonical and social-image URLs use the absolute production HTTPS origin. No PNG screenshot was substituted for the original artwork.

All four originals, the mobile derivative and social card were visually inspected. Both final EN/BG desktop/mobile screenshot sets and menu/reflection captures were read. Stylized 3D materials and some fine sampling grain remain, particularly in the skin scene; these are disclosed qualities of authored renders, not photographic or clinical claims. Generator scripts, source files and manifests remain unserved under tools/.
