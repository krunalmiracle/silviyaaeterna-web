# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: adults in Bulgaria and the Bulgarian diaspora who are curious about astrology, numerology, skincare and psychology-informed wellbeing, and who want calm, honest material in their own language. Secondary: parents looking for grounded, educational notes about children, family routines and adult self-improvement. Visitors arrive from a future YouTube channel or a shared link, in a browsing, evaluating state, and need to understand within seconds what this project is and what it is not.

## Product Purpose

Silviya Aeterna is a bilingual (Bulgarian and English) personal brand and content project, led by a future YouTube channel, covering six topic pillars: astrology, numerology, skincare, psychology-informed wellbeing, family and children, and mental health. This website exists to introduce the brand, publish the topic map, state the content boundaries honestly, and hold honest "coming soon" states until the channel and any shopping path exist. Success means a visitor leaves understanding the project, its topics, its limits, and where to return when the channel launches.

## Positioning

An unhurried personal project for curiosity and everyday care: reflection material with explicit boundaries (educational, never diagnosis, treatment or professional care), fully bilingual at launch, and honest about everything that does not exist yet. Symbolic traditions are clearly distinguished from scientific knowledge. No fake links, metrics or social proof.

## Operating Context

- Live production repo: `krunalmiracle/silviyaaeterna-web`, deployed by Dokploy from `main` to `silviyaaeterna.krusil.com`.
- Runtime: a single Bun process serving static files on port 3000 behind Traefik (Docker). No database, no auth, no third-party runtime services.
- Language: Bulgarian and English are equal; visitors switch languages on the page.

## Capabilities and Constraints

- Static, single-page site: HTML, CSS, one small JavaScript file, local original WebP still lifes, a raster social preview and a small SVG favicon. No runtime third-party requests.
- Accessible language toggle (keyboard operable, `aria-pressed`, `lang` attribute updated, preference remembered locally).
- Honest states only: no fake links, follower counts, videos, testimonials, qualifications, pricing, income claims, product claims, newsletter success or medical outcomes.
- No YouTube, social or Oriflame destinations exist yet; their sections are explicit coming-soon states with no href.
- Health and psychology material must be phrased as educational and reflective, never diagnosis, treatment or professional care; a concise disclaimer and a calm professional-help boundary are required.
- Security: the exposed AI web editor surface (write/generate/rollback endpoints, hard-coded S3 credentials, remote model calls) must be removed entirely; the server becomes a minimal static file server with security headers, an allow-list of servable paths, and no secrets or outbound network calls.
- Dev-only documents (PRODUCT.md, DESIGN.md, surface briefs, `.impeccable/`) must never be served by the web server.
- Must stay deployable by the existing Dockerfile/Bun command.

## Brand Commitments

- Brand and future YouTube channel name: **Silviya Aeterna** (fact; preserve exactly).
- Broad subject areas are fixed: astrology, numerology, skincare, psychology-informed wellbeing, family and children, adult self-improvement, mental health.
- Bilingual EN/BG parity at launch.
- The user authorized complete replacement and delegated design choice. The settled direction is Daylight Glasshouse: cool pale jade/leaf grounds, deep spruce type, restrained amber inside sunlit botanical/celestial still lifes. Self-hosted Cyrillic-capable Onest display with Geist supporting text. Broad raster art, open editorial chapters, no repeated cards, no navy/coral orbit-chart identity, no cream-luxury serif or purple glow. No em dashes in visible copy.
- User explicitly requested generated original assets. The approved production method is original locally authored 3D rendering, not stock, hotlinks or a claim of AI photography. Provenance and generation scripts stay dev-only under tools/.

## Evidence on Hand

- Previous navy/coral SVG almanac design is the anti-reference for this replacement. The already-hardened static server and port 3000 deployment contract are preserved unchanged.
- Brand name and six topics are settled. Original raster output is supplied by the independent glasshouse asset producer; only verified files are integrated, with the exact manifest retained under tools/.
- Absences future work must not fabricate: no YouTube channel URL, no social accounts, no Oriflame links, product details or pricing, no audience metrics, no testimonials, no credentials, no published videos.

## Product Principles

1. Say only what is true; where something does not exist yet, say so plainly.
2. Reflection, not prescription: everything is educational material for curious adults and families.
3. Two languages, one voice: Bulgarian and English carry identical content and standing.
4. Calm and unhurried: no urgency tricks, no hype, no dark patterns.
5. Own assets only: no stock imagery, no hotlinks, no third-party runtime dependencies.

## Accessibility & Inclusion

- Keyboard-complete navigation with visible focus; touch targets at least 44px.
- WCAG 2.1 AA contrast on the daylight jade palette; semantic landmarks and heading order; descriptive bilingual alt text.
- `prefers-reduced-motion` disables all entrance motion; content stays visible without JavaScript.
- Language switch exposed through `lang` and `aria-pressed`; no horizontal scrolling at 320, 390, 768, 1024 or 1440px. Theme anchors enhance native disclosures without hiding any of the six topic descriptions.
