# Narrow fixes after independent round 1

The attempted separate fix worker could not access file tools and made no changes. Its exact failure remains in `../fixer-cli.log`. The parent used its functioning file tools to apply the narrow fixes, with no changes to profiles, approval policy or shared providers. Independent re-review remains mandatory.

## Real regression sequence

`tools/verify_lifecycle.py red` ran against the unchanged failing candidate. It recorded 5/13 passed and 8 failed: restoration of frames/ScrollTriggers; post-return pause/ARIA/CSS/label; Bulgarian label; paused second return; resumed repeated return; reduced third return; desktop EN and BG artwork names. Mobile AX checks and actual persisted BFCache event checks already passed.

The initial AX assertion incorrectly assumed the flat CDP node list was document reading order. It was corrected to recursively traverse childIds before the authoritative red run above. No app change was made before that red run.

After fixes, `tools/verify_lifecycle.py green` recorded 13/13 passed, no page errors. Three actual native Back returns each retained a marker and reported persisted pageshow, not synthetic BFCache events. AX-tree traversal exposes exactly eight distinct bilingual image descriptions in document order at both 1440 and 390px.

## Exact changes

- `assets/scene.js`: named suspension/restore handlers, resource cleanup and nulling, RAF handle reset, observers reattached on persisted pageshow, actual hero intersection recomputed, user pause reread safely, scene selection and choreography resynchronized. Entrance completion remains preserved, preventing a replay. Context-loss handler removes itself during cleanup to avoid accumulating listeners across repeated restores. Nonpersisted navigation still cleans resources.
- `assets/styles.css`: enhanced desktop source chapter figures are visually clipped to one pixel, not display:none, retaining accessibility-tree meaning and normal source order. Decorative sticky clones remain aria-hidden. Mobile layout is unchanged.
- `assets/scene.js`: portable inverse smoothstep ramp replaces undefined reversed GLSL edges, with the same intended visual mask.
- `PRODUCT.md` and `.impeccable/surfaces/index-html.md`: remove obsolete glasshouse/Onest/local-3D/pending-implementation statements; record actual sanctuary and static mobile fallback without changing factual product content.
- `tools/verify_lifecycle.py`: repeatable actual BFCache and localized AX regression.
- `tools/verify_delivery.py`: requires the new green regression as well as existing evidence.

## Tests and cleanup

npm test passed after the patch; actual output is `npm-test.tap`. Red and green browser reports and screenshots are saved beside this handoff. The full browser and axe batches are rerun by the parent afterward; final aggregates belong in verification.json. No source/producer image, server/CSP, deployment or Git changes were made by the failed worker. All browser instances started by the regression script close in finally. The owner's preview server remains in use for re-review.

No independent pass or production deployment is claimed by this fix handoff.
