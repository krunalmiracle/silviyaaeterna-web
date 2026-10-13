# Asset provenance

Every visual asset in this directory is original work authored for this redesign. There is
no stock photography, no hotlinked image, no third-party illustration and no generated
photograph anywhere in the site.

| File | What it is | Origin |
| --- | --- | --- |
| `brand-mark.svg` | Crescent and coral sun brand mark | Authored procedurally, `tools/generate_assets.py` |
| `favicon.svg` | Simplified mark for the tab icon | Same generator |
| `hero-plate.svg` | Hero almanac chart (rings, orbits, ephemeris scale) | Same generator |
| `manifesto-plate.svg` | Moon phase row over sun-path arcs | Same generator |
| `topic-astrology.svg` | Twelve segment zodiac wheel | Same generator |
| `topic-numerology.svg` | Three by three number grid with life-path line | Same generator |
| `topic-skincare.svg` | Droplet over skin strata and ripples | Same generator |
| `topic-wellbeing.svg` | Topographic contour rings | Same generator |
| `topic-family.svg` | Linked circles under a protective arc | Same generator |
| `topic-mental-health.svg` | Night window with lamp glow and sill plant | Same generator |
| `channel-plate.svg` | Broadcast waves over a film strip | Same generator |
| `shop-plate.svg` | Unlabelled vessels under a hatched placeholder | Same generator |
| `safety-plate.svg` | Boundary brackets with a centre line | Same generator |
| `closing-plate.svg` | Crescent, coral sun and dawn arcs | Same generator |
| `social-og.svg` | 1200x630 social card | Same generator; embeds the subset Geist font as a data URI so the card keeps its typography |
| `social-og.png` | 1200x630 social delivery card | Rasterized locally from `social-og.svg` with FFmpeg for broad Open Graph crawler support |
| `fonts/Geist-Variable-subset.woff2` | Self-hosted variable typeface (latin, latin-ext, cyrillic) | Subset from the official `geist` npm package (SIL OFL 1.1) with fontTools; license in `fonts/OFL-1.1.txt` |

Generation record: run `python3 tools/generate_assets.py`. Geometry is seeded, so the output
is reproducible. Palette: ink `#060A17`, cobalt `#0E1B45` / `#12225C`, moonstone `#EDF1F8`,
mineral mint `#9FE7CE`, solar coral `#FF6B4A`.
