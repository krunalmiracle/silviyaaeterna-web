from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,PngImagePlugin
import json,hashlib
root=Path(__file__).resolve().parents[1]
source=Path('/opt/data/home/silviya-magic-assets/hero-garden.png')
with Image.open(source) as original: image=ImageOps.fit(original.convert('RGBA'),(1200,630))
shade=Image.new('RGBA',image.size)
draw=ImageDraw.Draw(shade)
for y in range(630):draw.line((0,y,1200,y),fill=(6,22,25,int(35+max(0,y-200)/430*130)))
image=Image.alpha_composite(image,shade)
draw=ImageDraw.Draw(image)
font=ImageFont.truetype(str(root/'tools/CormorantGaramond-source.ttf'),92)
small=ImageFont.truetype(str(root/'tools/CormorantGaramond-source.ttf'),40)
draw.text((70,395),'Silviya Aeterna',font=font,fill='#f3efe5')
draw.text((74,505),'A little more in tune.',font=small,fill='#e7c995')
metadata=PngImagePlugin.PngInfo();metadata.add_text('Source','Derivative of actual producer hero-garden.png; original SHA256 '+hashlib.sha256(source.read_bytes()).hexdigest());metadata.add_text('Derivation','1200x630 cover crop, contrast scrim, local Cormorant typography. No new scene generation.')
image.convert('RGB').save(root/'assets/social-og.png',pnginfo=metadata,optimize=True)
# A contact sheet of real browser captures, not constructed site output.
names=['astrology','numerology','skincare','wellbeing','family','mental-health']
sheet=Image.new('RGB',(1440,1350),'#081e22')
for i,name in enumerate(names):
 with Image.open(root/f'.impeccable/review/scene-{name}.png') as capture:
  capture.thumbnail((720,450));sheet.paste(capture,((i%2)*720,(i//2)*450))
sheet.save(root/'.impeccable/review/scenes-contact.png')
print('Real-artwork social derivative and six-capture contact sheet saved')
