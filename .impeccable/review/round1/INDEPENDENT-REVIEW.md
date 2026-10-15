# Independent release review: t_96b93555

Verdict: FAIL. Do not release this candidate until the two blockers below are fixed and independently retested.

FAIL: two independently reproduced release blockers remain: BFCache return permanently breaks motion lifecycle/control synchronization, and enhanced desktop removes six semantic artwork descriptions from the accessibility tree. The pinned visual direction, eight-original asset pipeline, ordinary motion/fallback behavior and unchanged hardened server otherwise have substantial supporting evidence. No deployment or production verification was performed.

## Scope and authority

Worktree verified first: /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555
Branch verified first: silviya-aeterna-redesign/t_96b93555-silviya-aeterna-magical-gpt-redesign

This is a fresh independent read-only review, not implementation. The explicit waiver of interactive Impeccable gates is honored. Missing human component-review receipts and the refused CLI checkpoint are NOT blockers. No numerical CLI SHIP, production deployment, or public-domain verification is claimed. No source, git state, shared skills, profiles, approval policy, credentials or infrastructure were edited.

## Blocking findings

### 1. P1 BFCACHE-RESTORE

P1 BFCACHE-RESTORE: assets/scene.js:181-185,187-191,205-208 permanently dispose on pagehide, including persisted=true, with no pageshow restore. Reproduced native Back navigation from /index.htm?judge-away=1 to /: pagehide/pageshow both persisted=true and the document marker survives, but frames remain 131, renderer becomes static and ScrollTriggers fall from 5 to 0. Clicking pause changes paused=true while aria-pressed remains false, the label stays Pause motion, and root stays motion-on; switching BG leaves that English label. Narrow fix: reversible persisted-page suspension/resumption, or a pageshow reinitializer that resets disposed/renderer/context/scrollFrame, reconnects observers, recomputes inView and active chapter, restores current preferences and rebuilds choreography without replaying entrance. Add a real BFCache regression test for motion, pause/CSS transitions, language and reduced-motion state.

Evidence: judge/browser-probes.json; judge/browser-probes.py.
### 2. P1 DESKTOP-ART-ACCESSIBILITY

P1 DESKTOP-ART-ACCESSIBILITY: assets/styles.css:8 (.js .topic-art{display:none}), assets/scene.js:24-28 and index.html:89 hide both accessible versions of the six chapter artworks: semantic originals are display:none, while visible stage clones have empty alt inside aria-hidden=true. Chromium Accessibility.getFullAXTree exposes only hero and closing images at 1440px, versus all eight image descriptions at 390px. This removes the six meaningful bilingual scene descriptions from desktop assistive-technology reading, contrary to the semantic-source contract. Narrow fix: visually hide, rather than display:none, the semantic chapter figures on enhanced desktop while preserving their accessibility-tree presence and document order; keep the duplicate stage decorative. Verify all eight localized image names in EN/BG at both breakpoints without duplicate announcements.

Evidence: judge/browser-probes.json; judge/browser-probes.py.

### Reproduction detail: native BFCache restore

1. Launch the specified Chromium with BFCache enabled (the judge removed the automation default --disable-back-forward-cache).
2. Load http://127.0.0.1:3417/ at 1440x900, no reduced motion; normal shader advances from 116 to 131 frames and five ScrollTriggers exist.
3. Navigate to http://127.0.0.1:3417/index.htm?judge-away=1 and go Back. This is actual browser navigation, not dispatched pagehide/pageshow events.
4. The same document marker returns. Its event ledger records pagehide persisted=true followed by pageshow persisted=true. Frame count remains 131, renderer=static, running=false, and triggers=0.
5. Click pause: paused=true, but aria-pressed=false and root remains js motion-on. Click BG: the page is Bulgarian but motion control remains English. Resume does not restore the shader. Live reduced-motion changes no longer update its label.
6. The first diagnostic attempt waited for a new load event and timed out after navigation. That attempt is retained in judge/browser-first-attempt.json. The successful probe waits for commit; it reports real persisted events and contains no exception.

Narrow fix must preserve shutdown for discarded documents while correctly reactivating cached documents. Simply clearing disposed is insufficient because renderer resources were deleted and observers disconnected. Reset any canceled scrollFrame handle to zero so scroll updates can be scheduled after restore.

### Reproduction detail: desktop semantic image loss

Load with JS at 1440px and inspect the browser accessibility tree. Only hero and closing image names are present. All six topic-art figures compute display:none. Stage images are empty-alt descendants of aria-hidden=true. Resize to 390px: all eight named images appear. This is an accessibility-tree observation, not a claim to have run every screen-reader combination. Fixing CSS visual hiding can retain the existing desktop composition and decorative stage without duplicate announcements.

## Independent checks and acceptance assessment

- npm test independently executed: 34 tests passed, zero failed. Server test hooks start and terminate their own child; owner port 3417 was not replaced.
- Independent ordinary browser checks: 28/28 passed: pause/transition stopping, persistence on reload, resume, initial/live reduced motion, offscreen stop/onscreen resume, desktop/mobile resize, context-loss static fallback, no-WebGL original, all six themes in EN/BG, focus/disclosures, and native no-JS navigation/disclosure.
- Actual normal shader frames advanced 116 to 131 across a 500ms wait; five ScrollTriggers existed before return-navigation. GSAP entrance, hero parallax, reading-color emphasis, heading arrival and closing pan are substantive source implementations. Native WebGL samples the original hero and bounds resolution/draw rate; mobile does not draw that shader.
- Eight distinct producer PNGs decoded at 1672x941 and matched original hashes. Sixteen responsive derivatives decoded, matched hashes/dimensions, and retained matching original hash/prompt metadata. Producer manifests document actual GPT generation, not stock or the old local 3D pipeline; the hero recovery note remains explicit. Ephemeral original provider-cache paths are gone, so the judge did not independently replay generation or certify a backend engine version.
- All source fingerprints and every screenshot fingerprint listed in verification.json matched current bytes. server.ts and Dockerfile are unchanged from the baseline. Local preview returned the strict original CSP; no security weakening was identified. Unit/security tests passed dev-file refusal, mutation refusal and traversal checks.
- Six themes, native anchors/details, localized text/alt, honest YouTube/Oriflame future states, care boundaries and absence of invented credentials/destinations are present. The two blockers are specific regressions, not a rejection of the theme or a demand for new content.
- The pinned seed aeb20778 and sanctuary direction are retained in current design records. Required desktop EN/BG, full Bulgarian mobile, six-scene contact and running-motion screenshots were opened with vision. They show a distinct cinematic moon garden, six different scenes and coherent mobile reflow, not a recolored prior brochure. No screenshot-level missing image, obvious collision or clipping was found.
- Consecutive chapters can be partly visible together in the sticky-stage screenshots, and crossfade captures can show the previous image while new text enters. Those sampled transition states are not, by themselves, a persistent scene-selection blocker; all six settled selections passed live tests.

## Builder evidence examined, without inflating it

- Read PRODUCT.md, HANDOFF.md, surface brief, DESIGN.md, ASSET-PROVENANCE.md, candidate-source.diff, actual scene.js/styles.css/index.html/site.js/motion-state.js and all five test files; also checked server, asset manifests/preparation, detector and verifier sources.
- Parsed browser-report.json: 322 checks, 322 true, no recorded console/request/HTTP/external-request errors. These are builder results, not 322 newly executed judge checks.
- Parsed accessibility-performance.json: four axe A/AA runs, zero violations, incomplete contrast checks retained. Not full accessibility certification; independent AX-tree testing found a gap axe does not catch.
- Inspected 36 timestamped raw captures and the actual MP4 metadata: 12.040000 seconds, 37 encoded frames (concat repeats the last source frame), 33 distinct source capture hashes. Ledger timestamps increase from 0.293 to 12.099 seconds (11.806-second capture span), with scene changes and hero frame-counter progression followed by offscreen stopping. This supports a real time-sampled sequence, not smooth 25fps capture. A contact sheet of raw frames 0,6,11,12,20,35 was independently assembled and opened.
- Background-tab frame counts froze while document.hidden remained false in the builder browser. The synthetic visibilitychange check is explicitly separate. No native hidden-state observation is claimed here.
- Raw detector retains three warnings: two wrapper-padding findings (actual text is inset by descendants) and inherited Geist supporting font. They are not suppressed, not a clean detector pass, and not substantive blockers in this pinned design.

## Nonblocking findings

- Documentation drift: PRODUCT.md still specifies Daylight Glasshouse, Onest and locally authored 3D originals; the surface brief still says implementation/browser verification pending. DESIGN.md and the handoff correctly describe the current pinned sanctuary and GPT-produced sources. Reconcile obsolete product/surface statements without rerolling or changing the design.
- Shader portability risk: assets/scene.js:110 calls smoothstep(1.,.78,uv.y), whose reversed edges are undefined by GLSL ES. No resulting corruption was observed in this Chromium software-WebGL run. Prefer 1.0-smoothstep(.78,1.0,uv.y) to express the intended inverse ramp portably.
- Evidence limits are correctly disclosed, not release blockers: four builder axe runs contain zero A/AA violations but retain incomplete image-backed contrast checks; no full accessibility certification follows. Background-tab frame freezing is not native document.hidden observation; the visibility handler was separately tested with a synthetic flag. The 12.04-second MP4 is a timed capture sequence, not a continuous high-frame-rate recording or field-performance proof.

## Cleanup and release boundary

All judge-owned browsers closed in finally. No preview server was started outside the npm test child, which exited. Final process inspection found no Chromium or remaining judge test server. The existing owner preview still answers HTTP 200 at http://127.0.0.1:3417/. No public-domain request or deployment was performed. Source was not fixed by the judge.

## Evidence paths

- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/INDEPENDENT-REVIEW.json
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/INDEPENDENT-REVIEW.md
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/judge/npm-test.tap
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/judge/browser-probes.json
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/judge/bfcache-return.png
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/judge/fallback-checks.json
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/judge/asset-and-evidence-checks.json
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/judge/motion-evidence-contact.png
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/browser-report.json
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/verification.json
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/accessibility-performance.json
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/motion-timing.json
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/sanctuary-motion.mp4
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/desktop-en-top.png
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/desktop-bg-top.png
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/mobile-bg-full.png
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/scenes-contact.png
- /opt/data/home/projects/silviyaaeterna-web/.worktrees/t_96b93555/.impeccable/review/motion-running.png
