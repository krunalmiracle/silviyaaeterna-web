# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: adults in Bulgaria and the Bulgarian diaspora who are curious about astrology, numerology, skincare and psychology-informed wellbeing, and who want calm, honest material in their own language. Secondary: parents looking for grounded, educational notes about children, family routines and adult self-improvement. Visitors arrive from a future YouTube channel or a shared link, in a browsing, evaluating state, and need to understand within seconds what this project is and what it is not.

## Product Purpose

Silviya Aeterna is a bilingual (Bulgarian and English) personal brand and content project, led by a future YouTube channel, covering six topic pillars: astrology, numerology, skincare, psychology-informed wellbeing, family and children, and mental health. This website exists to introduce the brand, publish the topic map, state the content boundaries honestly, and hold honest "coming soon" states until the channel and any shopping path exist. Success means a visitor leaves understanding the project, its topics, its limits, and where to return when the channel launches.

## Positioning

An unhurried, educational "living almanac" rather than a hype channel: reflection material with explicit boundaries (educational, never diagnosis, treatment or professional care), fully bilingual at launch, and honest about everything that does not exist yet. A neighbouring project could copy the topics, but not the combination of two-language parity, plain boundary-setting, and refusing to fake links, metrics or social proof.

## Operating Context

- Live production repo: `krunalmiracle/silviyaaeterna-web`, deployed by Dokploy from `main` to `silviyaaeterna.krusil.com`.
- Runtime: a single Bun process serving static files on port 3000 behind Traefik (Docker). No database, no auth, no third-party runtime services.
- Language: Bulgarian and English are equal; visitors switch languages on the page.

## Capabilities and Constraints

- Static, single-page site: HTML, CSS, one small JavaScript file, local SVG assets only.
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
- The brief pins the visual direction: a "Living Almanac" world, nocturnal cobalt/ink ground with mineral mint, moonstone and a restrained solar-coral accent; contemporary Geist-like sans; asymmetric hero; no cream-luxury serif, no purple AI glow, no black/pink carryover; one theme, one radius system, one accent logic; no em dashes in visible copy. (Visual detail lives in DESIGN.md; recorded here only as a binding commitment.)
- User explicitly requested generated original assets: hand-authored local SVG editorial illustrations instead of stock or hotlinks.

## Evidence on Hand

- Existing site in the repo (black/pink/purple serif look, Google Fonts, AI-editor `server.ts` with hard-coded credentials) is the anti-reference for this redesign, not an asset.
- Real assets that exist: the brand name, the topic list, and the locally authored SVG set in `assets/` (see `assets/PROVENANCE.md`).
- Absences future work must not fabricate: no YouTube channel URL, no social accounts, no Oriflame links, product details or pricing, no audience metrics, no testimonials, no credentials, no published videos.

## Product Principles

1. Say only what is true; where something does not exist yet, say so plainly.
2. Reflection, not prescription: everything is educational material for curious adults and families.
3. Two languages, one voice: Bulgarian and English carry identical content and standing.
4. Calm and unhurried: no urgency tricks, no hype, no dark patterns.
5. Own assets only: no stock imagery, no hotlinks, no third-party runtime dependencies.

## Accessibility & Inclusion

- Keyboard-complete navigation with visible focus; touch targets at least 44px.
- WCAG 2.1 AA contrast on the nocturnal palette; semantic landmarks and heading order; descriptive bilingual alt text.
- `prefers-reduced-motion` disables all entrance motion; content stays visible without JavaScript.
- Language switch announced through `lang` and `aria-pressed`; no horizontal scrolling at 390px or 1440px.
