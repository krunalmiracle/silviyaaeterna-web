# Product

<!-- impeccable:product-schema 1 -->

## Platform
web

## Users
Bulgarian Oriflame shoppers and prospective VIP customers or partners who want verified products, transparent joining terms and optional bilingual everyday-care notes.

## Product Purpose
Silviya Aeterna leads with eight individually verified Oriflame Bulgaria products, official photographs, dated EUR prices and exact product destinations. The official Oriflame Bulgaria store and separate VIP/partner registration routes are prominent. Silviya's invitation code or personal link is still unknown: generic official forms must not be described as crediting her. Four bilingual everyday-care themes support the commercial paths; a future YouTube channel is coming soon. No invented qualifications, income promises, testimonials or affiliate attribution.

## Operating Context
- Production repo: `krunalmiracle/silviyaaeterna-web`, Dokploy `main`, https://silviyaaeterna.krusil.com/.
- Minimal Bun static server on port 3000 behind Traefik; no database, auth, form, tracking, cookies or third-party runtime dependencies.
- EN/BG content parity, working language preference and navigation.

## Design Commitments
- The owner's latest direction is light by default with cool silver as the brand accent, not dark or gold.
- Six original daylight illustrations remain for editorial sections. Eight separate official Oriflame product photos are sourced from the corresponding public product pages, not generated or represented by the editorial art.
- No astrology, numerology, moonlit imagery, mystical claims or luminous shader on the published page.
- Accessible, high-contrast charcoal copy on airy off-white and pearl-grey surfaces, brushed-silver accents, local Cormorant Garamond and Geist fonts, restrained animation with pause and reduced-motion support.
- Description, alt text and interactive states remain equivalent in English and Bulgarian. The latest artwork, bilingual alternatives, dimensions, hashes, provider requests and sidecar provenance are in `tools/ASSET-MANIFEST.json` and `tools/ASSET-PROVENANCE.md`; PNG originals are archived outside the static server.
- Safety copy is educational and never a substitute for professional care. Product prices/stock are a dated snapshot, not a live checkout; the source evidence, SKUs and optimized-image hashes are in `tools/ORIFLAME-PRODUCTS.json`. The official partner form lists a €10 annual fee added to the first order and an optional invitation-code field. VIP registration is a distinct form. No generic link establishes a referral to Silviya.

## Accessibility and Release
- Preserve ordered headings, skip link, keyboard controls, 44px targets, responsive layout, useful content without JavaScript, reduced motion and no unintended third-party requests.
- Run `npm test` and the responsive browser review before release; inspect the actual live commit, image URLs, CSS and social preview after Dokploy deployment.
