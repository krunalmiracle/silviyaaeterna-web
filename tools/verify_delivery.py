#!/usr/bin/env python3
"""Read-only artifact checks; writes only a generated development verification report.
uv run --with pillow --with fonttools --with brotli python tools/verify_delivery.py
"""
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont
from html.parser import HTMLParser
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'.impeccable/review'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
class Page(HTMLParser):
    images=[]
    def handle_starttag(self,tag,attrs):
        if tag=='img': self.images.append(dict(attrs))
html=(ROOT/'index.html').read_text()
page=Page();page.feed(html)
manifest=json.loads((ROOT/'tools/ASSET-MANIFEST.json').read_text())
report={'verifiedAt':datetime.now(timezone.utc).isoformat(),'assets':[],'fonts':[],'screenshots':[]}
for entry in manifest['assets']:
    path=ROOT/'assets/images'/entry['filename']
    with Image.open(path) as im:
        im.load()
        assert im.size==(entry['width'],entry['height'])
        assert im.info.get('xmp')
        assert sha(path)==entry['sha256']
        tag=next(i for i in page.images if i['src'].endswith(entry['filename']))
        assert (int(tag['width']),int(tag['height']))==im.size
        assert tag['alt']==entry['alt']['en'] and tag['data-alt-bg']==entry['alt']['bg']
        report['assets'].append({'path':str(path.relative_to(ROOT)),'dimensions':list(im.size),'bytes':path.stat().st_size,'sha256':sha(path),'provenance':'original XMP retained; manifest hash and bilingual alt match'})
for name,dimensions in [('assets/images/hero-glasshouse-mobile.webp',(780,520)),('assets/social-og.png',(1200,630))]:
    path=ROOT/name
    with Image.open(path) as im:
        im.load();assert im.size==dimensions
        assert im.info.get('xmp') or im.info.get('Source')
        report['assets'].append({'path':name,'dimensions':list(im.size),'bytes':path.stat().st_size,'sha256':sha(path),'provenance':'embedded derivative origin retained'})
required={ord(c) for c in html if '\u0400'<=c<='\u04ff'}
for name in ['Onest-Variable.woff2','Geist-Variable-subset.woff2']:
    path=ROOT/'assets/fonts'/name
    font=TTFont(path)
    cmap=set().union(*(set(t.cmap) for t in font['cmap'].tables if t.isUnicode()))
    missing=required-cmap
    assert not missing, f'{name} missing {missing}'
    report['fonts'].append({'path':str(path.relative_to(ROOT)),'CyrillicCodepointsUsed':len(required),'missing':sorted(missing),'sha256':sha(path)})
browser=json.loads((REVIEW/'report.json').read_text())
assert browser['mode']=='full acceptance' and not browser['issues']
assert browser['checksPassed']==browser['checksTotal']
for name in browser['screenshots']:
    path=ROOT/name
    with Image.open(path) as im:
        im.load();assert min(im.size)>=390
        report['screenshots'].append({'path':name,'dimensions':list(im.size),'sha256':sha(path)})
tap=(REVIEW/'npm-test.tap').read_text()
report['tests']={key:int(re.search(r'# '+key+r' (\d+)',tap).group(1)) for key in ['tests','pass','fail']}
assert report['tests']=={'tests':32,'pass':32,'fail':0}
report['browserChecks']={'passed':browser['checksPassed'],'total':browser['checksTotal'],'imageCompleteRounds':2,'externalRequests':browser['externalRequests'],'failedRequests':browser['failedRequests'],'consoleErrors':browser['consoleErrors'],'httpErrors':browser['httpErrors'],'contrast':browser['contrast']}
report['sourceFingerprints']={name:sha(ROOT/name) for name in ['index.html','assets/styles.css','assets/site.js','server.ts','Dockerfile']}
report['sourceSnapshots']={p.name:sha(p) for p in (ROOT/'tools/glasshouse-source/source').iterdir() if p.is_file()}
renderer_hash=sha(ROOT/'tools/glasshouse-source/source/render_mitsuba.py')
assert all(e['source_script_sha256']==renderer_hash for e in manifest['assets'])
report['rendererSourceMatchesManifest']=True
report['sourceArchive']='/opt/data/home/silviya-glasshouse-assets/'
report['reviewScope']='Builder visual confirmation only; independent judge and production release are parent-owned.'
(REVIEW/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'tests':report['tests'],'browser':report['browserChecks'],'images':len(report['assets']),'fonts':report['fonts'],'screenshots':len(report['screenshots']),'rendererSourceMatchesManifest':True},indent=2))
