#!/usr/bin/env python3
"""Read-only audit of actual producer inputs and the interrupted comp round.
Run: uv run --with pillow python tools/verify_magic_inputs.py
Does not change producer assets or mark any design gate approved.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/opt/data/home/silviya-magic-assets')
OUT = ROOT / '.impeccable/review'
manifest = json.loads((SOURCE / 'ASSET-MANIFEST.json').read_text())
expected = {'hero-garden', 'astrology-moon', 'numerology-pattern', 'skincare-ritual',
            'psychology-journal', 'family-grove', 'mental-health-haven', 'closing-bloom'}
assets = []
for item in manifest['assets']:
    path = SOURCE / (item['id'] + '.png')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as image:
        image.load()
        size = list(image.size)
        metadata_keys = list(image.info)
    assets.append({'id': item['id'], 'path': str(path), 'sha256': digest,
                   'expectedSha256': item['sha256'], 'hashMatches': digest == item['sha256'],
                   'decoded': True, 'dimensions': size,
                   'dimensionsMatch': size == [item['width'], item['height']],
                   'metadataKeys': metadata_keys,
                   'promptPresentInManifest': bool(item.get('prompt')),
                   'provider': item.get('provider'), 'model': item.get('model'),
                   'imageSource': item.get('image_source'), 'integrated': False})
comps = []
for name in ['a', 'b', 'c']:
    path = ROOT / '.impeccable/mocks' / (name + '.png')
    receipt_path = Path(str(path) + '.json')
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    row = {'id': name, 'path': str(path.relative_to(ROOT)), 'exists': path.exists(),
           'receipt': str(receipt_path.relative_to(ROOT)), 'success': receipt.get('success'),
           'error': receipt.get('error'), 'approved': receipt.get('approved', False)}
    if path.exists():
        with Image.open(path) as image:
            image.load()
            row['dimensions'] = list(image.size)
        row['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        row['hashMatchesReceipt'] = row['sha256'] == receipt.get('sha256')
    comps.append(row)
report = {
    'status': 'blocked',
    'capturedAt': datetime.now(timezone.utc).isoformat(),
    'scope': 'Input/comp audit only. No new implementation or browser acceptance performed.',
    'blocker': "Codex Responses API HTTP 400: The 'gpt-5.5' model is not supported when using Codex with a ChatGPT account.",
    'providerCause': '/opt/hermes/plugins/image_gen/openai-codex/__init__.py:42 hard-codes _CODEX_CHAT_MODEL',
    'openPhase': 'comps', 'expectedOriginalCount': 8, 'actualOriginalCount': len(assets),
    'uniqueOriginalCount': len({a['id'] for a in assets}),
    'originalInventoryMatches': {a['id'] for a in assets} == expected,
    'assets': assets, 'comps': comps,
    'completedCompCount': sum(c['exists'] and c['success'] is True for c in comps),
    'requiredCompCount': 3, 'integratedOriginalCount': 0,
    'newWebsiteImplemented': False, 'independentReview': 'not performed',
    'browserAcceptance': 'not run; no new implementation',
    'motionEvidence': 'not produced; no new implementation',
    'productionRelease': 'not attempted',
    'producerFilesModified': False,
    'disclosures': [
        'Existing review screenshots and test reports from the prior Daylight Glasshouse implementation are not evidence for this task.',
        'DESIGN.md and design.json still describe the prior implementation; no new artifact exists to document.',
        'No shipping candidate or independent SHIP verdict exists.'
    ]
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'verification.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({k: report[k] for k in ['status', 'actualOriginalCount', 'originalInventoryMatches', 'completedCompCount', 'integratedOriginalCount', 'blocker']}, indent=2))
assert len(assets) == manifest['count'] == 8
assert report['originalInventoryMatches']
assert all(a['hashMatches'] and a['dimensionsMatch'] and a['decoded'] for a in assets)
assert all(c.get('hashMatchesReceipt', True) for c in comps)
