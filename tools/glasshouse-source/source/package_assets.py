"""Optimize actual renders, embed authored-render provenance, verify, and manifest."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, PngImagePlugin

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'source'
BRIEF = (SOURCE / 'ORIGIN.md').read_text()
METHOD = 'Original authored procedural 3D illustration; geometry authored with Blender 5.2.2 LTS, exported as PLY, then ray traced with Mitsuba 3.9.1 LLVM CPU, 64 samples, three threads, bounded tile queues. Mild OpenCV non-local-means denoising. No image-generation model, photography, stock, or external texture/geometry assets.'
ART = {
    'hero-glasshouse': {
        'dimensions': [1800, 1200], 'budget_bytes': 500000,
        'intent': 'Image-led editorial hero: sunlike amber glass orb on a honed mineral plinth; jade curved architectural screen; generous deep-green laurel leaves and fern; still water dish, daylight and soft window shadows. Tangible grown foliage rather than primitive decoration.',
        'alt_en': 'Amber glass sphere on a pale mineral plinth beside green foliage and a shallow water dish, framed by a curved jade wall.',
        'alt_bg': 'Кехлибарена стъклена сфера върху светъл минерален постамент до зелени листа и плитък съд с вода, пред извита нефритенозелена стена.',
        'crop_note': 'Keep the amber orb and right-hand foliage together. For mobile use the whole 3:2 image or object-position 55% 50%; avoid an extreme narrow portrait crop.'
    },
    'sky-study': {
        'dimensions': [1400, 1050], 'budget_bytes': 400000,
        'intent': 'Dreamlike celestial study: mottled chalk-mineral sphere on a squared plinth, thick refractive amber glass crescent, botanical branch and amber lens. Sculptural still life, not a diagram or real astronomical scene.',
        'alt_en': 'A pale mineral sphere and amber glass crescent on a stone platform, with leafy stems in soft daylight.',
        'alt_bg': 'Светла минерална сфера и кехлибарен стъклен полумесец върху каменна платформа, със зелени клонки на мека дневна светлина.',
        'crop_note': 'Prefer 4:3 or a centered 1:1 crop; retain the left botanical branch and right amber crescent.'
    },
    'skin-ritual': {
        'dimensions': [1400, 1050], 'budget_bytes': 400000,
        'intent': 'Tactile skincare ritual still life: unbranded hollow frosted glass vessel, pale porcelain water bowl, broad curved mesh leaves and a small amber glass disk on a honed mineral tray. No product, label, treatment or medical claim.',
        'alt_en': 'An unlabelled frosted vessel, a porcelain bowl of water and broad green leaves on a pale stone tray.',
        'alt_bg': 'Матиран съд без етикет, порцеланова купа с вода и широки зелени листа върху светъл каменен поднос.',
        'crop_note': 'Prefer the original 4:3 frame; centered square is usable if the leaf tip may crop.'
    },
    'quiet-growth': {
        'dimensions': [1400, 1050], 'budget_bytes': 400000,
        'intent': 'Inviting growth and rest still life: ribbed deep-spruce ceramic vase with generous branching green foliage, nested pale jade porcelain and amber vessels, calm sunlight and a curved jade screen. Family and growth are metaphors, not a depiction of real people.',
        'alt_en': 'A ribbed dark-green vase holding leafy branches beside nested pale ceramic and amber glass bowls.',
        'alt_bg': 'Оребрена тъмнозелена ваза с разлистени клонки до вложени една в друга светли керамични и кехлибарени стъклени купички.',
        'crop_note': 'Retain the upper canopy. Use 4:3 or object-position 48% 45% for a square crop.'
    }
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xmp_packet(name, intent):
    ET.register_namespace('x', 'adobe:ns:meta/')
    ET.register_namespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
    ET.register_namespace('glasshouse', 'https://silviyaaeterna.krusil.com/ns/asset-origin/1.0/')
    root = ET.Element('{adobe:ns:meta/}xmpmeta')
    rdf = ET.SubElement(root, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
    d = ET.SubElement(rdf, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
    d.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '')
    for field, val in [('title', name), ('description', METHOD+'\n\nAuthored render brief: '+intent+'\n\n'+BRIEF), ('source', 'source/render_mitsuba.py; source/export_scenes.py; source/render.py; source/ORIGIN.md; source/'+name+'.blend')]:
        ET.SubElement(d, '{http://purl.org/dc/elements/1.1/}'+field).text = val
    ET.SubElement(d, '{https://silviyaaeterna.krusil.com/ns/asset-origin/1.0/}method').text = 'authored-procedural-3d-render'
    ET.SubElement(d, '{https://silviyaaeterna.krusil.com/ns/asset-origin/1.0/}seed').text = '71426'
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def main():
    records = []
    for name, info in ART.items():
        src = SOURCE / (name+'.png')
        dest = ROOT / (name+'.webp')
        with Image.open(src) as raw:
            im = raw.convert('RGB')
        assert list(im.size) == info['dimensions'], (name, im.size)
        render = json.loads((SOURCE/(name+'-render.json')).read_text())
        origin = {'asset': name+'.webp', 'method': METHOD, 'authored_render_brief': info['intent'], 'shared_art_direction': BRIEF, 'image_model_prompt': None, 'source_script': 'source/render_mitsuba.py', 'geometry_scripts': ['source/render.py','source/export_scenes.py'], 'scene_file': 'source/'+name+'.blend', 'seed': 71426, 'render': render}
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('Title', name)
        metadata.add_text('Description', info['intent'])
        metadata.add_text('Origin', METHOD)
        metadata.add_text('AuthoredRenderBrief', info['intent']+'\n\n'+BRIEF)
        metadata.add_text('Source', 'source/render_mitsuba.py; source/export_scenes.py; source/render.py')
        im.save(src, pnginfo=metadata, optimize=True)
        xmp = xmp_packet(name, info['intent'])
        for quality in (94,92,90,88,85,82,78):
            im.save(dest, 'WEBP', quality=quality, method=6, xmp=xmp)
            if dest.stat().st_size < info['budget_bytes']:
                break
        assert dest.stat().st_size < info['budget_bytes'], (name, dest.stat().st_size)
        with Image.open(dest) as check:
            check.load()
            assert list(check.size) == info['dimensions']
            assert check.info.get('xmp') == xmp
            assert b'authored-procedural-3d-render' in check.info['xmp']
        # Sidecar follows full-filename-plus-.json convention.
        (ROOT/(name+'.webp.json')).write_text(json.dumps(origin,ensure_ascii=False,indent=2)+'\n')
        record = {
            'filename': dest.name, 'width': im.width, 'height': im.height,
            'bytes': dest.stat().st_size, 'sha256': sha(dest), 'format': 'image/webp',
            'quality': quality, 'budget_bytes': info['budget_bytes'],
            'engine': render['engine'], 'method': 'authored-procedural-3d-render',
            'provenance': METHOD, 'generation_intent': info['intent'],
            'alt': {'en': info['alt_en'], 'bg': info['alt_bg']},
            'source_script': 'source/render_mitsuba.py', 'source_script_sha256': sha(SOURCE/'render_mitsuba.py'),
            'geometry_scripts': ['source/render.py','source/export_scenes.py'],
            'source_geometry': 'source/geometry/', 'source_scene_description': 'source/'+name+'-scene.json',
            'source_brief': 'source/ORIGIN.md', 'source_scene': 'source/'+name+'.blend',
            'source_png': 'source/'+src.name, 'source_png_bytes': src.stat().st_size,
            'source_png_sha256': sha(src), 'prompt_sidecar': name+'.webp.json',
            'embedded_metadata': {'webp': 'XMP: authored render method, intent, shared brief and source', 'png': 'PNG text: Origin, AuthoredRenderBrief, Source'},
            'image_model_prompt': None, 'seed': 71426, 'render': render,
            'crop_note': info['crop_note']
        }
        records.append(record)
        print(json.dumps({k:record[k] for k in ('filename','width','height','bytes','quality')},ensure_ascii=False))
    manifest = {
        'collection': 'DAYLIGHT GLASSHOUSE / Silviya Aeterna',
        'provenance': METHOD,
        'image_generation_tool': 'No connected image-generation tool was exposed by this CLI; local bpy route used.',
        'palette': {'jade':'#E6EDE3','spruce':'#183F35','amber':'#C5913D'},
        'asset_count': len(records), 'total_webp_bytes': sum(r['bytes'] for r in records),
        'assets': records,
        'reproduction': {'script':'source/render_mitsuba.py','geometry_export':'source/export_scenes.py','packaging':'source/package_assets.py','command_document':'SUMMARY.md','dependencies':{'python':'3.13','bpy':'5.2.2','mitsuba':'3.9.1','pillow':'12.3.0','numpy':'see source/dependencies.txt','opencv-python-headless':'see source/dependencies.txt'},'render_device':'CPU','threads':3,'samples':64,'denoising':'OpenCV non-local means'},
        'boundaries': ['No portraits or people','No text or logos in artwork','No real product or location claim','No stock assets','No model-generated photographs','No website repo, deployment, profile, settings or credential changes'],
        'verification': {'decoded_all_webp':True,'exact_dimensions':True,'under_byte_budgets':True,'embedded_provenance_read_back':True,'visual_review':'See SUMMARY.md for the actual visual inspection and any correction pass.'}
    }
    (ROOT/'ASSET-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('PACKAGING_VERIFIED',json.dumps({'asset_count':len(records),'total_webp_bytes':manifest['total_webp_bytes']}))


if __name__ == '__main__':
    main()
