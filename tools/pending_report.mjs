import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const review = path.join(root, '.impeccable/review');
const layout = JSON.parse(await readFile(path.join(review, 'layout-only.json'), 'utf8'));
const findings = JSON.parse(await readFile(path.join(review, 'detect.json'), 'utf8'));
const tap = await readFile(path.join(review, 'npm-test.tap'), 'utf8');
const summary = {};
for (const key of ['tests','pass','fail']) summary[key] = Number(tap.match(new RegExp(`# ${key} (\\d+)`))?.[1]);
const report = {
  status: 'INCOMPLETE: pending independent original image input; do not deploy',
  recordedAt: new Date().toISOString(),
  worktree: root,
  branch: execFileSync('git',['branch','--show-current'],{cwd:root,encoding:'utf8'}).trim(),
  unitAndServerTests: {command:'npm test', ...summary, artifact:'.impeccable/review/npm-test.tap', expectedFailureCause:'All five failures are absent original image/social assets. Security, content and interaction tests pass.'},
  browser: {command:'uv run --with patchright python tools/shots.py --layout-only', mode:layout.mode, checksPassed:layout.checksPassed, checksTotal:layout.checksTotal, remainingIssues:layout.issues, artifact:'.impeccable/review/layout-only.json', screenshotRounds:0, screenshots:[], missingImageErrorsExpected:true, viewportSummary:layout.viewports.map(v=>({width:v.width,height:v.height,language:v.language,overflowX:v.overflowX,clipped:v.clipped,smallTargets:v.smallTargets})), contrast:layout.contrast},
  detector: {command:'/opt/data/skills/impeccable/scripts/impeccable detect --json index.html assets/styles.css assets/site.js', runs:1, primary:findings.filter(f=>!f.advisory).length, advisory:findings.filter(f=>f.advisory).length, artifact:'.impeccable/review/detect.json', residuals:[
    'Cramped-padding: static scanner does not resolve logical padding-block on chapter/about wrappers. Chapters use 64px/48px top padding; About uses 64-112px and shell gutters. Final rendered review remains pending.',
    'Overused-font: Geist is supporting text, expressly permitted by the brief; distinctive Onest owns all headings and the wordmark.',
    'Font-size advisories: small navigation/status/caption and responsive variant sizes are intentional; primary type roles are documented, not suppressed.'
  ]},
  originalImagesIntegrated: [],
  pendingInputs: ['hero-glasshouse.webp','sky-study.webp','skin-ritual.webp','quiet-growth.webp','ASSET-MANIFEST.json','SUMMARY.md'].map(n=>'/opt/data/home/silviya-glasshouse-assets/'+n),
  remainingAcceptance: ['Inspect all four delivered images visually; verify dimensions/alt and integrate them using tools/prepare_images.py.', 'Update all HTML intrinsic dimensions/srcset widths from actual image output if they differ; choose crops from real artwork.', 'Generate and inspect matching social PNG; retain truthful producer provenance.', 'Run npm test to 32/32.', 'Run full screenshot batch, inspect every EN/BG capture, fix material issues together and confirm once.', 'Update DESIGN.md/surface brief pending notes and complete exact-commit independent judge review through parent.'],
  boundary: {serverAndDockerUnchanged:true,pushed:false,deployed:false,nativeKanbanModified:false,independentReview:'Parent-owned, not performed'},
};
await writeFile(path.join(review, 'report.json'), JSON.stringify(report,null,2)+'\n');
const source=await readFile(path.join(root,'tools/Onest-source.ttf'));
console.log(JSON.stringify({tests:summary,browserChecks:layout.checksTotal,detector:report.detector,OnestSourceSHA256:createHash('sha256').update(source).digest('hex')},null,2));
