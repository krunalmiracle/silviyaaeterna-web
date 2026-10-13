---
name: Silviya Aeterna
description: Living Almanac, a nocturnal cobalt editorial system for a bilingual reflection brand.
colors:
  ink: "#060a17"
  ink-soft: "#080d1f"
  cobalt-field: "#0e1b45"
  cobalt: "#12225c"
  cobalt-soft: "#151b3d"
  moonstone: "#edf1f8"
  moonstone-dim: "#c3cbde"
  mineral-mint: "#9fe7ce"
  solar-coral: "#ff6b4a"
  solar-coral-hover: "#ff8763"
  hairline: "rgba(159, 231, 206, 0.18)"
  hairline-strong: "rgba(159, 231, 206, 0.34)"
typography:
  display:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(2.85rem, 7.2vw, 5.5rem)"
    fontWeight: 600
    lineHeight: 0.96
    letterSpacing: "-0.038em"
  headline:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(1.9rem, 3.3vw, 3rem)"
    fontWeight: 600
    lineHeight: 1.04
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(1.2rem, 1.5vw, 1.45rem)"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Geist, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "normal"
rounded:
  surface: "14px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "40px"
  section: "clamp(60px, 9vh, 112px)"
components:
  button-primary:
    backgroundColor: "{colors.solar-coral}"
    textColor: "{colors.ink}"
    rounded: "{rounded.surface}"
    padding: "0 26px"
    height: "52px"
  button-primary-hover:
    backgroundColor: "{colors.solar-coral-hover}"
    textColor: "{colors.ink}"
    rounded: "{rounded.surface}"
    padding: "0 26px"
    height: "52px"
  lang-idle:
    backgroundColor: "transparent"
    textColor: "{colors.moonstone-dim}"
    rounded: "{rounded.surface}"
    padding: "0 10px"
    height: "44px"
  lang-active:
    backgroundColor: "{colors.solar-coral}"
    textColor: "{colors.ink}"
    rounded: "{rounded.surface}"
    padding: "0 10px"
    height: "44px"
  atlas-cell:
    backgroundColor: "{colors.ink-soft}"
    textColor: "{colors.moonstone}"
    rounded: "{rounded.surface}"
    padding: "clamp(20px, 2vw, 28px)"
---

# Design System: Silviya Aeterna

## Overview

**Creative North Star: "The Living Almanac"**

The page is an almanac spread read at night: a nocturnal cobalt ground, engraved line work,
moon phases and ephemeris rules, and one warm signal colour for anything that asks to be
acted on. It is a personal brand surface for reflection content, so it stays calm, slow and
editorial rather than promotional. Density is light (VISUAL_DENSITY 3): generous section
rhythm, one idea per section, and long-form text measures capped at 65ch.

The system is committed to one theme. Every section sits on the same ink ground; the channel
and shop sections step up to a cobalt field inside that same family rather than flipping to a
second theme. Asymmetry carries the personality: the hero is a weighted two-column split with
the plate dropped below the text baseline, the topic atlas is a twelve column bento with
uneven spans, and the closing section lets its illustration bleed off the right edge.

**Key Characteristics:**

- One accent (solar coral) reserved for action and focal points, never for decoration.
- Geist as the single family across display and body, two weights only (600 / 400-500).
- One radius value (14px) on every framed surface and control.
- Hairlines instead of shadows: 1px mint-tinted rules organise the page.
- Original SVG almanac plates, one per major section, all generated locally.
- Motion is a single authored reveal: blur-and-settle on the hero plate, quiet fade-up
  elsewhere, fully disabled under `prefers-reduced-motion`.

## Colors

The palette is nocturnal and cool, with exactly one warm note that only ever means "act" or
"look here".

### Primary

- **Solar Coral** (#ff6b4a): the only accent. Primary buttons, the active language button,
  and one focal element inside every illustration (the sun, the highlighted cell, the lamp).
- **Solar Coral Hover** (#ff8763): hover state of the primary button only.

### Secondary

- **Mineral Mint** (#9fe7ce): line work, hairlines, section rules, focus rings, illustration
  strokes, and secondary labels such as the safety list terms. It never fills a large area.

### Neutral

- **Ink** (#060a17): page ground and text on coral.
- **Ink Soft** (#080d1f): menu panel and default atlas cell fill.
- **Cobalt Field** (#0e1b45): illustration grounds, cobalt section bands, plate backing.
- **Cobalt** (#12225c): upper stop of the top-of-page radial wash and field gradients.
- **Cobalt Soft** (#151b3d): tinted atlas cell and raised band.
- **Moonstone** (#edf1f8): headings and primary text.
- **Moonstone Dim** (#c3cbde): body copy, navigation, notes.
- **Hairline** (rgba(159, 231, 206, 0.18)) and **Hairline Strong** (0.34): dividers,
  borders, plate frames.

### Named Rules

**The Coral Rule.** Solar coral appears only where the visitor can act or where an
illustration needs one focal point. Never as a section background, never as body text, never
as a decorative dot.

**The One Ground Rule.** All text sits on ink or a cobalt field from the same family. A light
section, a second accent hue, or a warm cream surface is out of system.

## Typography

**Display Font:** Geist (self-hosted variable subset, latin + latin-ext + cyrillic, OFL 1.1)
**Body Font:** Geist, same file.

**Character:** A contemporary Geist-like sans used at two weights. Hierarchy comes from size
and weight, never from colour tricks or gradient text. Bulgarian and English set in the same
face; the subset carries full Cyrillic so both languages keep identical texture.

### Hierarchy

- **Display** (600, clamp(2.85rem, 7.2vw, 5.5rem), 0.96, -0.038em): hero H1 only, two lines maximum.
- **Headline** (600, clamp(1.9rem, 3.3vw, 3rem), 1.04, -0.03em): section headings.
- **Title** (600, clamp(1.2rem, 1.5vw, 1.45rem), 1.25, -0.02em): atlas pillar headings.
- **Body** (400, 17px, 1.6): paragraphs, capped at 65ch.
- **Label** (500, 0.95rem, 1.4): navigation, notes, footer links.

### Named Rules

**The Two-Weight Rule.** 600 for headings and controls, 400/500 for everything else. No
third weight, no italic display, no uppercase eyebrows above headings.

## Layout

Container: `min(100% - 2 * gutter, 1240px)` with `gutter: clamp(20px, 4vw, 56px)`. Sections
separate with a single hairline and `padding-block: clamp(60px, 9vh, 112px)`, so there is
always more space above a heading than below it.

- **Header:** sticky, 64px, hairline bottom, translucent ink with backdrop blur (solid ink
  under `prefers-reduced-transparency`). Desktop: brand, five nav links, EN/BG toggle on one
  line. At 900px the nav collapses to a native `<details>` disclosure panel (works without
  JavaScript), keeping the language toggle beside it.
- **Hero:** two columns, 1.1fr / 0.9fr, `align-items: center`; the plate carries an extra
  top offset so the composition stays asymmetric. Below 900px it stacks to one column with a
  16/10 plate.
- **Atlas:** twelve columns, uneven spans (7/5, 5/7, 4/8) so no row is a repeated pair. Cell
  one is media-led, cell six splits horizontally with its copy centred. Below 900px every
  cell spans the full width.
- **Channel:** full-width plate band, then a 62ch text block.
- **Shop:** 380px side rail plus text; both columns stretch to one shared height.
- **Safety:** one framed panel, full-bleed image band on top, then a two column definition
  list with a single top hairline per row.
- **Closing:** illustration absolutely positioned off the right edge behind the copy; static
  16/9 plate below 900px.
- **Breakpoints in use:** 1040px (nav tightening), 900px (stacking / disclosure), 560px
  (type and full-width buttons).

## Elevation & Depth

The system is flat by default. Depth comes from tonal steps (ink → ink-soft → cobalt field)
and from hairlines, not from shadows.

### Shadow Vocabulary

- **Menu panel** (`box-shadow: 0 18px 44px rgba(3, 6, 16, 0.6)`): the only shadow in the
  system; it separates the mobile disclosure panel from the page beneath it.
- **Header veil** (`backdrop-filter: blur(10px)` over rgba(6, 10, 23, 0.92)): keeps section
  content legible under the sticky header. Removed under `prefers-reduced-transparency`.

### Named Rules

**The Flat Surface Rule.** Cards, plates and panels are flat at rest. No glow, no colored
halo, no hard offset shadow.

## Shapes

One radius system: **14px** (`--radius`) on every framed surface and control: buttons,
language buttons, plates, atlas cells, the safety panel, the mobile menu, the disclosure
summary. Nothing on the page uses a second radius except the 4px focus ring outline offset.
Borders are 1px: mint hairlines for structure, dashed moonstone for honest placeholder states.

## Components

### Buttons

- **Shape:** 14px radius, 52px tall, 26px horizontal padding, Geist 600 at 1.02rem.
- **Primary:** coral fill (#ff6b4a) with ink text (#060a17), 7:1 contrast. Hover lifts 1px
  and warms to #ff8763; active presses 1px down and scales 0.99.
- **Focus:** 2px mint outline, 3px offset, on `:focus-visible` for every interactive element.
- **Secondary / status ("soon state"):** not a control. A dashed moonstone hairline with
  moonstone-dim text, non-focusable, non-clickable, so an honest placeholder never reads as a
  dead button.

### Chips / Status

Dashed border (rgba(195, 203, 222, 0.45)) on a 3% moonstone wash, 14px radius, 52px tall.
Used only for "Channel launching soon" and "Details coming later".

### Cards / Containers

- **Corner style:** 14px.
- **Background:** ink-soft at 55% or a cobalt gradient for alternating cells.
- **Border:** hairline (rgba(159, 231, 206, 0.18)); plates use hairline-strong.
- **Internal padding:** clamp(20px, 2vw, 28px).
- **Shadow strategy:** none (see Elevation).

### Navigation

Desktop links are 0.95rem, moonstone-dim, 44px tall hit areas with 13px horizontal padding,
hovering to moonstone on a 9% mint wash. The active language button is coral with ink text
(`aria-pressed`). The mobile disclosure uses a 44px bordered square with two CSS bars that
cross into an X when open.

### Language Toggle

Two 46x44px buttons, 14px radius, 6px gap. Idle: transparent with hairline-strong border.
Active: coral with ink text. It updates `document.documentElement.lang`, the page title, every
`data-en` / `data-bg` string and every image `alt`, and remembers the choice in
`localStorage` (`sa-lang`).

### Illustration Plate

A framed figure (14px radius, hairline-strong border, cobalt-field backing) holding a local
SVG with `object-fit: cover`. Every major section owns exactly one plate; provenance lives in
`assets/PROVENANCE.md`.

## Do's and Don'ts

### Do:

- **Do** keep solar coral for actions and single focal points only.
- **Do** use 14px on every framed surface and control, without exception.
- **Do** separate sections with one mint hairline and clamp(60px, 9vh, 112px) of padding.
- **Do** set both languages in the self-hosted Geist subset; never add a webfont request.
- **Do** keep entrance motion to the hero plate blur-and-settle plus quiet fade-ups, and
  disable all of it under `prefers-reduced-motion`.
- **Do** frame unavailable features as dashed, non-interactive status chips.

### Don't:

- **Don't** add a second accent hue, a light section, or a cream surface.
- **Don't** use shadows, glows, gradient text, or a hard offset shadow for depth.
- **Don't** put an eyebrow or section number above a heading.
- **Don't** write an em dash or en dash anywhere in visible copy.
- **Don't** link to a channel, social account or shop that does not exist yet.
- **Don't** hide content behind an entrance animation that JavaScript might never complete.
