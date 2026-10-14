---
name: Silviya Aeterna
description: Daylight Glasshouse, a pale jade botanical editorial system.
colors:
  jade: "#e6ede3"
  leaf: "#f2f6ef"
  spruce: "#183f35"
  muted: "#466255"
  amber: "#c5913d"
  line: "#a8bbab"
  spruce-hover: "#285344"
typography:
  display:
    fontFamily: "Onest, sans-serif"
    fontSize: "clamp(3.2rem, 6.7vw, 6rem)"
    fontWeight: 500
    lineHeight: 1.02
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Onest, sans-serif"
    fontSize: "clamp(2.2rem, 4.2vw, 3.8rem)"
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: "-0.035em"
  chapter:
    fontFamily: "Onest, sans-serif"
    fontSize: "clamp(2rem, 3.6vw, 3.2rem)"
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: "-0.035em"
  title:
    fontFamily: "Onest, sans-serif"
    fontSize: "clamp(1.45rem, 2vw, 1.9rem)"
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Geist, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
rounded:
  surface: "6px"
spacing:
  small: "12px"
  medium: "24px"
  large: "40px"
  gutter: "clamp(20px, 4vw, 64px)"
  section: "clamp(64px, 8vw, 112px)"
components:
  primary-action:
    backgroundColor: "{colors.spruce}"
    textColor: "{colors.leaf}"
    rounded: "{rounded.surface}"
    padding: "12px 20px"
    height: "54px"
  primary-action-hover:
    backgroundColor: "{colors.spruce-hover}"
    textColor: "{colors.leaf}"
  language-active:
    backgroundColor: "{colors.spruce}"
    textColor: "{colors.leaf}"
    rounded: "{rounded.surface}"
    height: "44px"
    width: "44px"
  reflection-open:
    backgroundColor: "{colors.leaf}"
    textColor: "{colors.muted}"
    rounded: "{rounded.surface}"
    padding: "8px 18px 18px"
---

# Design System: Silviya Aeterna

## Overview

Creative North Star: Daylight Glasshouse.

Cool, leaf-tinted daylight surrounds confident sans-serif lettering and generous original botanical still lifes. The interface is open editorial space, not a collection of cards. Imagery carries physical depth; text and controls remain simple and legible.

Key characteristics:
- Pale jade owns the page; spruce carries both meaning and action.
- Onest display lettering and Geist supporting text are self-hosted and Cyrillic-capable.
- Broad, gently cornered imagery alternates with open reading space.
- Native disclosures offer reflection without making basic content dependent on scripts.

Implementation documentation is extracted from the final code and two bounded image-complete browser rounds. All four original still lifes and the derived social preview are integrated and visually inspected. This records builder verification, not independent judge approval.

## Colors

Primary: spruce for headings, controls, selection and focus. Spruce-hover only changes the primary action's hover state.

Secondary: amber is a restrained botanical/celestial accent in art and favicon, never low-contrast body text.

Neutral: jade is the principal ground; leaf is the lighter About field and open reflection background. Muted spruce supports body text. Line organizes chapters without outlining containers.

The Daylight Rule: choose cool green space over cream, navy or a dark-mode variant. The original navy/coral system is superseded.

## Typography

Onest brings rounded geometric confidence to display and section headings; Geist keeps long passages quiet. Both font files are local. tools/verify_delivery.py verified every Cyrillic codepoint used in the page against both shipping font cmaps; no glyph was missing.

The hero is two lines, capped at 6rem, with mobile sizing at 12.2vw and a 2.7rem compact override. Body text is normally 16px/1.6, rising to 18px in hero/About on larger screens. Paragraphs cap at 68ch, with narrower topic columns for paired art. Headings balance; no tracked uppercase labels or invented section numbers.

Supporting sizes in the actual system: intro 17px; desktop navigation and reflection copy .95rem; disclosure/status/safety .9rem; language .875rem; captions/footer .8rem (.75rem mobile art captions). Utility headings are 25px for future destinations, 26px for safety and 22px for mobile navigation; future names reduce to 23px on mobile. These subordinate and responsive roles explain the retained detector type-ramp advisories, rather than making every size a global display step.

## Layout

Content container: min(100% minus two gutters, 1320px). Sticky header is 88px on desktop, 76px at 800px and below. Anchor headroom is 110px.

The opening places a large left heading beside a shorter description/action, then one panoramic image. Three chapters pair images and two topics without cards. The middle chapter reverses its desktop columns. At 600px chapters become a linear heading, art, then topic passage.

Breakpoints: 1050px for tighter gaps; 800px for native mobile navigation and tablet image proportions; 600px for single-column reading; 350px for compact gutters and type. Section rhythm grows from 64px to 112px. Future destinations share two concise rows; safety is a compact concluding note.

Image treatment: the 1800x1200 hero fills a broad 320-440px-high desktop frame at 50% 53%. On mobile it is 290px high (270px at compact width), cropped at 55% 50% to retain sphere and foliage, with a 780x520 source candidate. The three 1400x1050 chapter originals occupy ratios 1.12, 1.3 and 1.06 on desktop; tablets use 1.12 and phones 1.1. All use real intrinsic dimensions and cover fitting. The remaining crops retain each scene's meaningful subjects; no graphic substitutes are used.

## Elevation & Depth

Depth comes from the original still lifes, not UI effects. Only the mobile navigation has a shadow: 0 16px 24px #183f3514. The sticky header is opaque jade, without backdrop blur. No card shadows or glow.

The single motion moment gently brightens an already-visible hero image over .8s with cubic-bezier(.16,1,.3,1). Reduced motion removes it entirely. All text stays visible regardless of JavaScript or animation state.

## Shapes

Small consistent 6px corners on controls, art, focus outlines and expanded reflections. Open topics have only a bottom divider. CSS chevrons indicate disclosure direction; authored inline SVG arrows mark navigation. No decorative glyph icons.

## Components

Primary action: spruce/leaf, 54px minimum height, 12px by 20px padding, authored down arrow. Hover changes only fill. Focus on all controls is a 2px spruce outline with 5px offset; the skip link uses amber on spruce.

Language selector: two 44px buttons; active spruce fill and aria-pressed. It updates document language, page title, visible strings, alt text and accessible labels, and remembers sa-lang locally. Storage failure does not disable it.

Navigation: native details disclosure on narrow screens, 44px summary target, 52px links. Two bars become a conventional close X when open. Escape closes and restores summary focus; selecting a destination closes the panel. Theme links retain normal anchor behavior while selecting a topic, opening its native prompt and moving focus to its article. Other topic descriptions remain visible.

Reflection: native details beneath each complete topic description. Closed summaries are at least 44px; open passages use the leaf field with 18px inset. No fake links, loading states, article controls or unreachable destinations.

Coming-soon status: plain noninteractive text aligned with the real destination name. Never styled as an inactive purchase/watch button.

## Do's and Don'ts

Do preserve Cyrillic parity, daylight contrast, 44px controls and readable content without scripts.
Do make the original raster still lifes decisive, with descriptive alt text and documented provenance.
Do retain the single corner language and open editorial rhythm.
Don't reuse the old almanac diagrams, dark palette, rounded card grid or oversized disclaimer panel.
Don't imply that rendered vessels are branded products, the scene is a real location, or the project provides clinical services.
Don't hide content behind entrance animation or fabricate channel/shop destinations.
