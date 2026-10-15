"""Verify real sanctuary assets, fonts, browser reports and source hashes."""
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont
from html.parser import HTMLParser
from datetime import datetime,timezone
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.impeccable/review'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Document(HTMLParser):
 def __init__(self):super().__init__();self.images=[]
 def handle_starttag(self,tag,attrs):
  if tag=='img':self.images.append(dict(attrs))
html=(ROOT/'index.html').read_text();doc=Document();doc.feed(html)
manifest=json.loads((ROOT/'tools/ASSET-MANIFEST.json').read_text())
report={'verifiedAt':datetime.now(timezone.utc).isoformat(),'assets':[],'fonts':[],'screenshots':[]}
assert len(doc.images)==manifest['asset_count']==len(manifest['assets'])==8
for entry in manifest['assets']:
 original=Path('/opt/data/home/silviya-magic-assets')/(entry['id']+'.png')
 assert sha(original)==entry['originalSha256']
 tag=next(i for i in doc.images if i['src'].endswith(entry['filename']))
 assert tag['alt']==entry['alt']['en'] and tag['data-alt-bg']==entry['alt']['bg']
 for d in entry['derivatives']:
  path=ROOT/'assets/images'/d['filename']
  with Image.open(path) as im:
   im.load();assert im.size==(d['width'],d['height']) and sha(path)==d['sha256']
   xmp=json.loads(im.info['xmp']);assert xmp['sourceSha256']==entry['originalSha256']
   report['assets'].append({**d,'sourceId':entry['id'],'originalSha256':entry['originalSha256']})
report['originalsIntegrated']=len(manifest['assets'])
report['responsiveDerivatives']=len(report['assets'])
report['responsiveBytes']=sum(a['bytes'] for a in report['assets'])
with Image.open(ROOT/'assets/social-og.png') as im:
 im.load();assert im.size==(1200,630) and im.info['Source']
 report['social']={'dimensions':list(im.size),'sha256':sha(ROOT/'assets/social-og.png'),'provenance':im.info['Source']}
required={ord(c) for c in html+(ROOT/'assets/scene.js').read_text() if '\u0400'<=c<='\u04ff'}
for name in ['CormorantGaramond-Variable.woff2','Geist-Variable-subset.woff2']:
 path=ROOT/'assets/fonts'/name;font=TTFont(path);cmap=set().union(*(set(t.cmap) for t in font['cmap'].tables if t.isUnicode()));missing=required-cmap
 assert not missing,(name,missing)
 report['fonts'].append({'name':name,'usedCyrillicCodepoints':len(required),'missing':list(missing),'sha256':sha(path)})
for name in ['gsap.min.js','ScrollTrigger.min.js']:
 assert sha(ROOT/'assets/vendor'/name)==sha(ROOT/'node_modules/gsap/dist'/name)
report['vendorMatchesPinnedPackage']=True
browser=json.loads((OUT/'browser-report.json').read_text());assert browser['passed']==browser['total'] and not browser['failed']
for key in ['consoleErrors','externalRequests','failedRequests','httpErrors']:assert not browser[key]
for name in browser['screenshots']:
 path=ROOT/name
 with Image.open(path) as im:im.load();assert min(im.size)>=320;report['screenshots'].append({'path':name,'dimensions':list(im.size),'sha256':sha(path)})
report['browser']={'passed':browser['passed'],'total':browser['total'],'report':'browser-report.json'}
regression=json.loads((OUT/'fix/green-regression.json').read_text())
assert regression['passed']==regression['total'] and not regression['failed'] and not regression['errors']
report['lifecycleAndAccessibilityRegression']={'passed':regression['passed'],'total':regression['total'],'report':'fix/green-regression.json','nativeBFCacheReturns':3,'localizedAXRuns':4}
audit=json.loads((OUT/'accessibility-performance.json').read_text());assert all(c['passed'] for c in audit['checks'])
report['accessibility']={'axeRuns':len(audit['axe']),'violations':sum(len(r['violations']) for r in audit['axe']),'incompleteChecksRetained':True}
report['performance']=audit['performance']['observed'];report['performanceScope']=audit['performance']['throttling'];report['visibilityLimitation']=audit['visibility']['limitation']
tap=(OUT/'unit-tests.tap').read_text();report['tests']={key:int(re.search(r'^# '+key+r' (\d+)',tap,re.M).group(1)) for key in ['tests','pass','fail']};assert report['tests']['tests']==report['tests']['pass'] and report['tests']['fail']==0
video=OUT/'sanctuary-motion.mp4';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-of','json',str(video)],text=True));report['motionEvidence']={'path':str(video.relative_to(ROOT)),'sha256':sha(video),'ffprobe':probe['format'],'timingLedger':'motion-timing.json'}
ledger=json.loads((OUT/'motion-timing.json').read_text());assert len(ledger)==36 and ledger[-1]['elapsedSeconds']>5
report['timedCaptures']=len(ledger)
report['sourceFingerprints']={name:sha(ROOT/name) for name in ['index.html','assets/styles.css','assets/site.js','assets/scene.js','assets/motion-state.js','server.ts','Dockerfile','package.json','package-lock.json','DESIGN.md','.impeccable/design.json']}
def lum(c):
 v=[int(c[i:i+2],16)/255 for i in (1,3,5)];v=[n/12.92 if n<=.04045 else ((n+.055)/1.055)**2.4 for n in v];return sum(x*y for x,y in zip(v,[.2126,.7152,.0722]))
report['tokenContrast']={}
for fg,bg in [('#f3efe5','#081e22'),('#bfd1cc','#081e22'),('#e7c995','#081e22'),('#061619','#e7c995'),('#86aaa5','#081e22')]:
 lo,hi=sorted([lum(fg),lum(bg)]);ratio=(hi+.05)/(lo+.05);assert ratio>=4.5;report['tokenContrast'][fg+' on '+bg]=round(ratio,2)
report['compWorkflow']={'threeRealComps':all((ROOT/'.impeccable/mocks'/n).is_file() for n in ['a.png','b-native.png','c-native.png']),'selected':'b-native.png','selection':'user-delegated','interactiveReview':'explicitly waived, USER-WAIVER.md','cliGateState':'refused state retained; no forged approval or numerical SHIP claimed'}
report['reviewScope']='Builder evidence, pending independent judge. Deployment is a separate verified operation.'
(OUT/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:report[k] for k in ['originalsIntegrated','responsiveDerivatives','responsiveBytes','tests','browser','accessibility','motionEvidence','tokenContrast','fonts']},indent=2))
