from pathlib import Path
import json
import hashlib
from PIL import Image, PngImagePlugin
root = Path(__file__).resolve().parents[1]
source = Path('/opt/data/home/silviya-magic-assets/hero-garden.png')
receipt = json.loads(Path(str(source)+'.json').read_text())
out = root/'assets/plates/garden.png'
out.parent.mkdir(parents=True,exist_ok=True)
with Image.open(source) as image:
    image.load()
    native = image.size
    result = image.resize((2508,1412),Image.Resampling.LANCZOS)
    info = PngImagePlugin.PngInfo()
    info.add_text('generation_prompt',receipt['prompt'])
    info.add_text('origin',json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'nativeDimensions':native,'derivation':'Lanczos resample for comp plate gate; no new detail, not a comp crop','provider':'openai-codex','requestedModel':receipt['model']}))
    result.save(out,pnginfo=info)
print(json.dumps({'output':str(out),'native':native,'derived':[2508,1412],'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
