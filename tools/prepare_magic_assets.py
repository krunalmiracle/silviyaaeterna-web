"""Build responsive derivatives from eight read-only GPT originals."""
from pathlib import Path
import hashlib,json,shutil
from PIL import Image
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/opt/data/home/silviya-magic-assets')
manifest=json.loads((SOURCE/'ASSET-MANIFEST.json').read_text())
assert manifest['count']==len(manifest['assets'])==8
out=ROOT/'assets/images';out.mkdir(exist_ok=True)
assets=[]
for item in manifest['assets']:
    original=SOURCE/(item['id']+'.png')
    assert hashlib.sha256(original.read_bytes()).hexdigest()==item['sha256']
    with Image.open(original) as im:
        im.load(); assert im.size==(item['width'],item['height'])
        record={**item,'filename':item['id']+'.webp','originalSha256':item['sha256'],'alt':{'en':item['alt_en'],'bg':item['alt_bg']},'derivatives':[]}
        for width,suffix in [(1672,''),(780,'-small')]:
            size=(width,round(im.height*width/im.width))
            path=out/(item['id']+suffix+'.webp')
            metadata={'origin':'Actual producer GPT artwork; OAuth requested model does not prove backend engine','prompt':item['prompt'],'sourceSha256':item['sha256'],'sourceDimensions':im.size,'derivation':'Lanczos resize and WebP compression; no compositing'}
            im.convert('RGB').resize(size,Image.Resampling.LANCZOS).save(path,'WEBP',quality=87,method=6,xmp=json.dumps(metadata,ensure_ascii=False).encode())
            with Image.open(path) as check:check.load();assert check.size==size
            row={'filename':path.name,'width':size[0],'height':size[1],'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            record['derivatives'].append(row)
            if not suffix:record.update({k:row[k] for k in ['sha256','width','height']})
        assets.append(record)
(ROOT/'tools/ASSET-MANIFEST.json').write_text(json.dumps({'asset_count':8,'assets':assets},indent=2,ensure_ascii=False)+'\n')
font=TTFont(ROOT/'tools/CormorantGaramond-source.ttf');font.flavor='woff2';font.save(ROOT/'assets/fonts/CormorantGaramond-Variable.woff2')
vend=ROOT/'assets/vendor';vend.mkdir(exist_ok=True)
for name in ['gsap.min.js','ScrollTrigger.min.js']:
    shutil.copyfile(ROOT/'node_modules/gsap/dist'/name,vend/name)
license_path=ROOT/'node_modules/gsap/LICENSE'
if license_path.exists():shutil.copyfile(license_path,vend/'GSAP-LICENSE.txt')
print(json.dumps({'originals':len(assets),'derivatives':sum(len(a['derivatives']) for a in assets),'imageBytes':sum(d['bytes'] for a in assets for d in a['derivatives']),'fontBytes':(ROOT/'assets/fonts/CormorantGaramond-Variable.woff2').stat().st_size},indent=2))
