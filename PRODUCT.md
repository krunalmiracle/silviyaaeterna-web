# Product

<!-- impeccable:product-schema 1 -->

## Platform
web

## Users
Adults and families who want practical bilingual notes on skincare, everyday wellbeing, family conversations and mental health.

## Product Purpose
Silviya Aeterna is an English/Bulgarian personal project covering four everyday themes. It links to the current official Oriflame Bulgaria catalogue and registration while stating that these are not confirmed personal referral links. A future YouTube channel is marked as coming soon. No invented qualifications, outcomes, testimonials or affiliate association.

## Operating Context
- Production repo: `krunalmiracle/silviyaaeterna-web`, Dokploy `main`, https://silviyaaeterna.krusil.com/.
- Minimal Bun static server on port 3000 behind Traefik; no database, auth, form, tracking, cookies or third-party runtime dependencies.
- EN/BG content parity, working language preference and navigation.

## Design Commitments
- The owner's latest direction is light by default with cool silver as the brand accent, not dark or gold.
- Six original, separate daylight images illustrate the hero, skincare, wellbeing, family, mental health and closing section. They are illustrative scenes rather than photos of Silviya, specific Oriflame products or a medical service.
- No astrology, numerology, moonlit imagery, mystical claims or luminous shader on the published page.
- Accessible, high-contrast charcoal copy on airy off-white and pearl-grey surfaces, brushed-silver accents, local Cormorant Garamond and Geist fonts, restrained animation with pause and reduced-motion support.
- Description, alt text and interactive states remain equivalent in English and Bulgarian. The latest artwork, bilingual alternatives, dimensions, hashes, provider requests and sidecar provenance are in `tools/ASSET-MANIFEST.json` and `tools/ASSET-PROVENANCE.md`; PNG originals are archived outside the static server.
- Safety copy is educational and never a substitute for professional medical or mental-health care. Catalogue and registration link to https://bg.oriflame.com/ and https://bg.oriflame.com/join-us/self-registration, without attributing a referral to Silviya.

## Accessibility and Release
- Preserve ordered headings, skip link, keyboard controls, 44px targets, responsive layout, useful content without JavaScript, reduced motion and no unintended third-party requests.
- Run `npm test` and the responsive browser review before release; inspect the actual live commit, image URLs, CSS and social preview after Dokploy deployment.
