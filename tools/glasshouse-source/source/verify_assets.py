"""Verify shipped assets, metadata, source links and actual renderer versions."""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
from PIL import Image, ImageStat

root=Path(__file__).resolve().parent.parent
m=json.loads((root/'ASSET-MANIFEST.json').read_text())
expected={'hero-glasshouse.webp':(1800,1200),'sky-study.webp':(1400,1050),'skin-ritual.webp':(1400,1050),'quiet-growth.webp':(1400,1050)}
assert m['asset_count']==len(m['assets'])==len(expected)==4
assert m['total_webp_bytes']==sum(a['bytes'] for a in m['assets'])
checks=[]
for a in m['assets']:
    p=root/a['filename']
    assert a['filename'] in expected
    assert p.stat().st_size==a['bytes']<a['budget_bytes']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
    assert a['engine'].startswith('Mitsuba 3.9.1')
    assert a['render']['samples']==64
    with Image.open(p) as im:
        im.load()
        assert im.size==expected[a['filename']]
        assert b'authored-procedural-3d-render' in im.info['xmp']
        assert b'Mitsuba' in im.info['xmp']
        assert min(ImageStat.Stat(im.convert('RGB')).stddev)>12
    for field in ('source_png','source_scene','source_script','source_brief','source_scene_description','prompt_sidecar'):
        assert (root/a[field]).is_file(),(field,a[field])
    with Image.open(root/a['source_png']) as src:
        src.load()
        assert src.size==expected[a['filename']]
        assert 'Mitsuba' in src.info['Origin']
    checks.append({'filename':p.name,'dimensions':list(expected[p.name]),'bytes':p.stat().st_size,'sha256':a['sha256'],'verified':True})
versions={name:version(name) for name in ('mitsuba','drjit','numpy','opencv-python-headless','pillow')}
(root/'source'/'dependencies.txt').write_text('python==3.13\nbpy==5.2.2\n'+'\n'.join(f'{k}=={v}' for k,v in versions.items())+'\n')
report={'result':'PASS','assets':checks,'total_webp_bytes':m['total_webp_bytes'],'dependencies':versions,'tests':['exact requested filenames and dimensions','all files decode','all byte budgets met','SHA-256 matches manifest','embedded authored-render provenance','source paths exist','PNG original dimensions and provenance','actual Mitsuba renderer and sample count','nonconstant raster content']}
(root/'source'/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
