---
name: Silviya Aeterna
description: Enchanted botanical sanctuary. A moonlit illustrated garden and living atlas.
colors:
  ink: "#081e22"
  deep: "#061619"
  surface: "#102c30"
  pearl: "#f3efe5"
  muted: "#bfd1cc"
  gold: "#e7c995"
  line: "#486362"
typography:
  display:
    fontFamily: "Sanctuary, serif"
    fontSize: "clamp(64px, 6.9vw, 119px)"
    fontWeight: 300
    lineHeight: 1.03
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Sanctuary, serif"
    fontSize: "clamp(44px, 5vw, 76px)"
    fontWeight: 400
    lineHeight: 1.03
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Geist, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.65
    letterSpacing: "normal"
rounded:
  control: "40px"
spacing:
  gutter: "clamp(20px, 4.7vw, 80px)"
  section: "clamp(90px, 10vw, 160px)"
components:
  primary-action:
    backgroundColor: "{colors.gold}"
    textColor: "{colors.deep}"
    rounded: "{rounded.control}"
    padding: "12px 25px"
    height: "52px"
---

# Enchanted botanical sanctuary

## Direction and authority

This replaces the Daylight Glasshouse aesthetic completely. Seed `aeb20778` is retained; the user's pinned sanctuary, not a newly rolled theme, is authoritative. Quiet wonder comes from actual GPT-produced garden artwork, continuous moonlit scenery, editorial lettering and deliberate motion. Nothing implies a real location, branded skincare product, clinical service or working shop.

Three image comps were generated and opened. B, the reflection-led composition, was selected under delegated design authority. Its region map and typography measurements are in `.impeccable/build`. The user explicitly waived interactive Impeccable gates, choosing “Waive interactive Impeccable approval gates; finish, test, independently review, and deploy to the domain.” The CLI cannot represent that waiver and remains at its refused human review checkpoint. We do not claim a signed human component approval or numerical Impeccable SHIP. The comp guides hierarchy, while original art and verified responsive usability determine the actual implementation.

## Color and type

Deep petrol is the canvas, pearl the display text, a quiet blue-green the supporting copy, and pale gold the interaction accent. This is not a recolored jade card layout. Art provides the luminous and natural color range; UI surfaces stay simple.

`Sanctuary` is the local CSS name for Cormorant Garamond, a variable OFL font. Its 300-weight display was chosen after font-match ranked it closest to the generated headline. That measured reason is the exception to avoiding familiar display defaults. Geist remains the legible supporting face. Both are self-hosted with Cyrillic glyphs; font coverage is checked from actual files.

The desktop hero is 6.9vw capped at 119px, matching the measured large display role. At 900px and below it becomes 9vw; below 600px it becomes 14vw, with a 49px compact floor. Other headings use 44–76px, topic headings 44–72px desktop / 45px mobile. Body text is generally 16px, with 15px mobile hero and 13px safety text. No giant labels, numbered faux chapters or tracked uppercase eyebrows.

## Composition

A full-height first viewport preserves the garden arch, distant lake and reflecting water. Live centered text occupies the lower middle of the scene; a pale gold action leads to the atlas. The small six-link row is desktop-only, while all devices retain real anchor navigation in the atlas.

The opening is followed by a two-column reading interlude and the atlas introduction. Above 900px, a sticky left image stage changes across six right-column topic passages. Each passage is about 85svh, allowing an image and reflective question to be read without a pinned-scroll trap. All six remain in normal document flow. The stage uses real originals, not canvas-rendered replacement scenes.

At 900px and below, the sticky stage disappears. Each original is shown with its own text, using alternating full-width and inset crops. Image aspect ratios vary between 1.15 and 1.5 to preserve subject meaning. Mobile doesn't pretend to be a squeezed desktop scroller. A final floating blossom carries the upcoming YouTube and Oriflame notices. Both are honest, noninteractive future states. Safety is calm and legible; the wordmark closes the page.

## Assets and provenance

Eight read-only producer originals are represented in the HTML and in `tools/ASSET-MANIFEST.json`:

- hero-garden: arch, lake and pool, first viewport.
- astrology-moon: moonlit lake and jasmine.
- numerology-pattern: patterned stones in rippling water.
- skincare-ritual: unbranded jar and vessel.
- psychology-journal: open notebook by an arch.
- family-grove: sapling among older trees.
- mental-health-haven: quiet sheltered chair.
- closing-bloom: floating flower in water.

Each has 1672px and 780px WebP derivatives, original SHA-256, actual dimensions, bilingual alt text, prompt and XMP provenance. The production art is a derivative of the independent producer scene, never a screenshot of generated UI. Social preview is a documented crop of the same hero with live-composed branding. No stock, Picsum, local 3D stand-ins, generated credentials or destinations.

## Motion system

The motion is substantive but subordinate to reading:

1. Local GSAP 3.13.0 introduces the hero with a 3.2-second art settle and staggered type/action movement. No text depends on an animation completing to become present.
2. ScrollTrigger creates restrained desktop hero parallax, scroll-linked text-color emphasis in the reading interlude, heading arrival and a closing-image pan.
3. The desktop atlas crossfades and gently settles each actual image as the active passage changes. Its six anchors continue to work without the enhancement.
4. One native WebGL renderer adds low-amplitude refraction and four restrained luminous points to the lower 45% of the hero. Resolution caps at 1672 CSS-pixel width times at most 1.25 DPR; drawing caps near 30fps. It samples the original hero, creates no 3D substitute, and never captures input.

The motion toggle has persistent explicit pause, translated labels, aria-pressed, and a 44px-or-larger target. `prefers-reduced-motion` is honored initially and on changes. Pause kills GSAP context animations and freezes the shader. The hero renderer stops drawing offscreen, on hidden visibility events, context loss and pagehide. Native BFCache pageshow restores cleaned resources and observers, preserves entrance completion, rereads pause preference, and resynchronizes labels, CSS and ScrollTriggers. The original image remains the fallback; mobile never initializes WebGL. Reduced motion retains content and instantaneous scene selection. No-JS keeps the complete page and native disclosure/navigation behavior.

## Accessibility and resilience

One h1, ordered h2/h3 structure, descriptive bilingual alt, visible focus, skip link, native details, semantic anchors, and readable static content are preserved. Desktop source figures are visually clipped rather than display:none, so all eight localized image descriptions remain in reading order while sticky-stage duplicates stay decorative. Theme navigation opens the relevant reflection and transfers focus. Active navigation follows scroll position. The narrow-screen navigation supports Escape with focus restoration, outside click and closing on selection.

All runtime resources are local. The static server and hardened CSP are unchanged: no inline scripts/styles, outbound network, backend, forms, analytics or third-party font/animation CDNs. DOM property styles used by GSAP do not require weakening the CSP.

## Evidence and limits

`browser-report.json`, `accessibility-performance.json`, `verification.json`, actual screenshots and `sanctuary-motion.mp4` contain measured evidence. The video is encoded from actual timestamped browser captures; it is not fabricated animation output. Four axe language/device combinations are checked. Image-backed text still needs visual review, and axe incomplete results are retained, not called full accessibility certification.

Local performance readings are not field benchmarks. In the background-tab automation test Chromium left document.hidden false, but actual frame counters stopped; the visibilitychange handler was separately exercised with an explicit synthetic flag. This limitation is disclosed rather than hidden. Builder evidence is not independent review; the separate judge's artifact supplies that verdict.
