# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: adults in Bulgaria and the Bulgarian diaspora looking for practical, bilingual notes on skincare, everyday wellbeing, family conversations and mental health. Visitors can also reach the current Oriflame Bulgaria catalogue and official registration, clearly identified as direct Oriflame links rather than Silviya's unconfirmed personal links.

## Product Purpose

Silviya Aeterna is a bilingual (Bulgarian and English) personal content project covering four everyday topics: skincare, wellbeing, family and children, and mental health. It uses practical questions and honest boundaries rather than symbolic traditions or unsupported promises. The site also links to Oriflame Bulgaria's official catalogue and registration, without implying these links belong to Silviya. A future YouTube channel remains a clearly labelled coming-soon item.

## Positioning

A calm personal project for everyday care, with clear educational boundaries and no invented qualifications, results or endorsements. Bulgarian and English carry equal content. Oriflame actions lead to Oriflame Bulgaria directly; a personal referral link has not been supplied.

## Operating Context

- Live production repo: `krunalmiracle/silviyaaeterna-web`, deployed by Dokploy from `main` to `silviyaaeterna.krusil.com`.
- Runtime: a single Bun process serving static files on port 3000 behind Traefik (Docker). No database, no auth, no third-party runtime services.
- Language: Bulgarian and English are equal; visitors switch languages on the page.

## Capabilities and Constraints

- Static, single-page site: HTML, CSS, local language/navigation and scene JavaScript, self-hosted GSAP/ScrollTrigger, eight original GPT-produced garden scenes as responsive WebPs, a raster social preview and a small SVG favicon. One bounded native WebGL hero effect has a static fallback. No runtime third-party requests.
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
- The user authorized complete replacement and delegated design choice. The pinned direction is an enchanted botanical sanctuary, seed aeb20778: moonlit garden, deep petrol, pearl display and champagne controls. A reflection-led hero leads through six illustrated scenes. Self-hosted Cyrillic-capable Cormorant Garamond display and Geist supporting text; no repeated cards or static green polish pass. No em dashes in visible copy.
- User explicitly required actual GPT-produced original artwork and rejected stock, Picsum and local 3D stand-ins. Eight read-only producer PNGs are integrated via hash-verified WebP derivatives. Prompts, requested model and exact-engine uncertainty are documented honestly. Provenance and helpers stay dev-only under tools/.

## Evidence on Hand

- Both the navy/coral SVG almanac and pale jade Daylight Glasshouse are superseded anti-references. The already-hardened static server, strict CSP and port 3000 deployment contract are preserved unchanged.
- Brand name and six topics are settled. Eight actual GPT-produced originals are integrated and hash-verified against tools/ASSET-MANIFEST.json as sixteen responsive derivatives. The 1200x630 social PNG is a documented hero crop with local typography. Original source archive remains read-only at /opt/data/home/silviya-magic-assets. Three real comps, measured region/font records, browser evidence and motion captures are retained under .impeccable/.
- Absences future work must not fabricate: no YouTube channel URL, no social accounts, no Oriflame links, product details or pricing, no audience metrics, no testimonials, no credentials, no published videos.

## Product Principles

1. Say only what is true; where something does not exist yet, say so plainly.
2. Reflection, not prescription: everything is educational material for curious adults and families.
3. Two languages, one voice: Bulgarian and English carry identical content and standing.
4. Calm and unhurried: no urgency tricks, no hype, no dark patterns.
5. Own assets only: no stock imagery, no hotlinks, no third-party runtime dependencies.

## Accessibility & Inclusion

- Keyboard-complete navigation with visible focus; touch targets at least 44px.
- WCAG 2.1 AA contrast on the actual dark sanctuary palette; semantic landmarks and heading order; all eight descriptive bilingual image alternatives remain in the accessibility tree at desktop and mobile.
- Initial and changing `prefers-reduced-motion`, persistent manual pause, offscreen/hidden suspension, BFCache restoration and no-WebGL/context-loss fallback are required. Mobile uses static original art. Content remains visible without JavaScript.
- Language switch exposed through `lang` and `aria-pressed`; no horizontal scrolling at 320, 390, 768, 1024 or 1440px. Theme anchors enhance native disclosures without hiding any of the six topic descriptions.
