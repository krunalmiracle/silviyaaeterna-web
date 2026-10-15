# Asset provenance: magical sanctuary

## Real sources, not substitutes

The eight producer PNG originals live read-only at `/opt/data/home/silviya-magic-assets`. `tools/ASSET-MANIFEST.json` records every original SHA-256, producer prompt, requested model, original dimensions, EN/BG alt and derivative hashes. These are actual generated raster originals, not local 3D, stock, placeholder URLs or synthesized API output. The previous glasshouse renders are removed from public assets; their historical development files are excluded from the Docker context.

The producer's requested model was GPT Image 2 high. This is a request/provenance fact, not a claim that the server disclosed its engine version. The native ChatGPT OAuth route used for comps B and C is server-managed; it did not return an exact image model. Those receipts explicitly say so. No claim of verified Image 2.5 or Sol-generated art is made.

## Production derivatives

`tools/prepare_magic_assets.py` reads and verifies all eight originals without modifying them. It produces 1672px and 780px WebP variants with Pillow Lanczos and quality 87. Each XMP payload records source hash, dimensions, prompt and derivative method. It performs no content substitution or scene compositing. Total image transfer bytes are computed in the verification report, not guessed.

The HTML contains eight semantic source images, including hero and closing, with responsive srcset and meaningful bilingual alt. Desktop's six-image sticky stage clones the actual chapter images for presentation only. Mobile and no-JS show the original figure alongside each passage. Seven images are lazy-loaded in source; hero has high priority.

The scene correspondences are: hero-garden, astrology-moon, numerology-pattern, skincare-ritual, psychology-journal, family-grove, mental-health-haven, closing-bloom.

`tools/prepare_magic_social.py` crops the original hero to 1200×630, applies a documented contrast scrim and local font lettering, and embeds its source hash in PNG metadata. It does not regenerate the artwork. The social title is “Silviya Aeterna”.

## Comps and measured reference

A was generated through the then-installed OAuth provider. B and C use the current upstream native OAuth provider loaded in a task-local helper. Three successful image outputs and receipts are under `.impeccable/mocks`. Earlier failed attempts are retained as failures. Builder visually inspected all three; B was selected under user-delegated design choice.

`.impeccable/build/regions.json` is the measured first-viewport map, with crop inspection and font-ranking receipts. The prepared large plate is a Lanczos-resampled independent hero original; it adds no generated detail and is not extracted from a UI mock. Its upsampling is explicitly disclosed in its metadata. The production page uses efficient original-resolution WebP derivatives instead.

The user waived mandatory interactive review checkpoints. This is not a signed component-review approval, and the CLI's refused state is retained. No numerical comp-match or independent SHIP is invented.

## Fonts and local animation

- Cormorant Garamond variable TTF: `https://raw.githubusercontent.com/google/fonts/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf`. Actual downloaded source retained at `tools/CormorantGaramond-source.ttf`, converted to WOFF2 with fontTools/Brotli. OFL retained beside the shipping font.
- Geist WOFF2 and its OFL are inherited local project assets. No new origin is invented for them.
- GSAP and ScrollTrigger 3.13.0 are pinned in package-lock, copied from the installed npm package's dist directory. Their embedded copyright/license headers remain intact. GSAP uses its standard license, not the fonts' OFL. No CDN is contacted at runtime.
- The native water shader is local authored code sampling only hero-garden.webp. It generates motion, not replacement artwork.

## Actual evidence and limitations

`verification.json` hashes all derivatives, fonts, source files and screenshots and checks Cyrillic coverage. `browser-report.json` records real responsive/bilingual interactions and fallback states. `scenes-contact.png` assembles six real scrolled desktop captures; it is not a replacement site screenshot. `sanctuary-motion.mp4` encodes timestamped actual browser frames, with `motion-timing.json` retaining capture timings.

Screenshots were opened with vision. Four axe desktop/mobile and EN/BG runs found no A/AA violations; incomplete checks are retained. Actual background-tab frame production stopped, but automation kept document.hidden false, so native hidden-state observation is not claimed. The explicit visibility handler was additionally tested with a synthetic hidden flag. Performance numbers are local unthrottled measurements, not real-user performance claims.

There is no claim of clinical credentials, guaranteed outcomes, a real depicted location, branded product endorsement, or a live YouTube/store destination.
