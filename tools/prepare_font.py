from pathlib import Path
from fontTools.ttLib import TTFont
import re, json
root = Path(__file__).resolve().parents[1]
font = TTFont(root / 'tools/Onest-source.ttf')
codepoints = set().union(*(set(t.cmap) for t in font['cmap'].tables if t.isUnicode()))
text = (root / 'index.html').read_text()
required = {ord(c) for c in text if '\u0400' <= c <= '\u04ff'}
missing = required - codepoints
assert not missing, f'Missing Cyrillic: {missing}'
font.flavor = 'woff2'
font.save(root / 'assets/fonts/Onest-Variable.woff2')
print(json.dumps({'font': 'Onest', 'Cyrillic_codepoints_used': len(required), 'missing': sorted(missing), 'woff2_bytes': (root / 'assets/fonts/Onest-Variable.woff2').stat().st_size}))
