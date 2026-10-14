"""Low-memory original ray-traced render of authored geometry with Mitsuba 3.
No image model or photographic input. Procedural textures generated locally.
"""
import argparse
import json
import math
from pathlib import Path
import time
import numpy as np
from PIL import Image, ImageFilter
import mitsuba as mi
import drjit as dr
import cv2

mi.set_variant('llvm_ad_rgb')
dr.set_thread_count(3)
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'source'
T=mi.ScalarTransform4f


def textures():
    rng=np.random.default_rng(71426)
    total=np.zeros((1024,1024),dtype=np.float32)
    for size,weight in [(8,.3),(32,.22),(128,.2),(512,.18),(1024,.1)]:
        a=(rng.random((size,size))*255).astype('uint8')
        total+=np.asarray(Image.fromarray(a).resize((1024,1024),Image.Resampling.BICUBIC),dtype=np.float32)/255*weight
    # Cool mottled mineral albedo, authored from seeded multiscale noise.
    low=np.array([.47,.55,.47]);high=np.array([.82,.86,.78])
    tex=low[None,None,:]+(high-low)[None,None,:]*np.clip((total-.24)*2.1,0,1)[...,None]
    Image.fromarray((tex*255).astype('uint8')).save(SOURCE/'mineral-procedural.png')


def bsdf(m):
    c=m['color'];name=m['name']
    if m['transmission']>.5:
        # Physical surface refraction; slightly tinted amber glass without a glow.
        col=[.98,.82,.43] if 'amber' in name else [.97,.995,.98]
        return {'type':'roughdielectric','distribution':'ggx','alpha':max(.015,m['roughness']**2),'int_ior':m['ior'],'ext_ior':1.0,'specular_transmittance':{'type':'rgb','value':col}}
    if 'leaf' in name or 'stem' in name or 'rib' in name:
        reflectance={'type':'rgb','value':[min(1,x*1.1) for x in c]}
        return {'type':'twosided','material':{'type':'roughplastic','diffuse_reflectance':reflectance,'alpha':.18,'int_ior':1.4}}
    if 'celestial' in name:
        reflectance={'type':'bitmap','filename':str(SOURCE/'mineral-procedural.png')}
    else:
        reflectance={'type':'rgb','value':c}
    return {'type':'twosided','material':{'type':'roughplastic','diffuse_reflectance':reflectance,'alpha':m['roughness']*.6,'int_ior':1.45}}


def area(origin,target,sx,sy,power,color):
    return {'type':'rectangle','to_world':T.look_at(origin=origin,target=target,up=[0,1,0])@T.scale([sx,sy,1]),'emitter':{'type':'area','radiance':{'type':'rgb','value':[power*x for x in color]}}}


def scene_dict(meta,w,h,crop=None):
    cam=meta['camera']
    film={'type':'hdrfilm','width':w,'height':h,'rfilter':{'type':'tent'},'sample_border':True}
    if crop:
        x,y,cw,ch=crop
        film.update(crop_offset_x=x,crop_offset_y=y,crop_width=cw,crop_height=ch)
    d={'type':'scene','integrator':{'type':'path','max_depth':8,'rr_depth':5,'hide_emitters':True},
       'sensor':{'type':'orthographic','to_world':T.look_at(origin=cam['origin'],target=cam['target'],up=[0,0,1])@T.scale([cam['scale']/2]*2+[1]),'sampler':{'type':'independent','sample_count':8},'film':film},
       'ambient':{'type':'constant','radiance':{'type':'rgb','value':[.24,.32,.27]}},
       'key':area([-3.8,-4,7.4],[0,0,.5],1.7,2.25,9,[1,.94,.82]),
       'fill':area([4,-1,5],[0,0,1],2.5,2.5,1.8,[.82,.93,1]),
       'rim':area([1.5,4,6],[0,0,1],1.5,1.5,7,[1,.98,.9])}
    for i,m in enumerate(meta['geometry']):
        d['mesh_'+str(i)]={'type':'ply','filename':str(ROOT/m['ply']),'bsdf':bsdf(m)}
    return d


def filmic(a):
    a=np.maximum(a,0)*.9
    # Explicit ACES-like display curve, followed by standard sRGB encoding.
    a=np.clip((a*(2.51*a+.03))/(a*(2.43*a+.59)+.14),0,1)
    return np.where(a<=.0031308,12.92*a,1.055*np.power(a,1/2.4)-.055)


def render(name,spp,scale):
    meta=json.loads((SOURCE/(name+'-scene.json')).read_text())
    w,h=round(meta['width']*scale),round(meta['height']*scale)
    output=np.zeros((h,w,3),dtype=np.float32)
    started=time.monotonic()
    # Cropped films bound live ray queues; never build a full-frame spp wavefront.
    tile=384
    scene=None
    for y in range(0,h,tile):
        for x in range(0,w,tile):
            cw,ch=min(tile,w-x),min(tile,h-y)
            scene=mi.load_dict(scene_dict(meta,w,h,(x,y,cw,ch)))
            accum=np.zeros((ch,cw,3),dtype=np.float32)
            passes=max(1,math.ceil(spp/8))
            for p in range(passes):
                image=mi.render(scene,seed=71426+p*17+y*3+x,spp=8)
                accum+=np.array(image,copy=True)[...,:3]/passes
                del image
                dr.sync_thread()
            output[y:y+ch,x:x+cw]=accum
            del scene
            dr.flush_malloc_cache()
            print(name,'tile',x,y,'seconds',round(time.monotonic()-started,1),flush=True)
    srgb=(filmic(output)*255+.5).astype('uint8')
    suffix='' if scale==1 else '-preview'
    dest=SOURCE/(name+suffix+'.png')
    # Mild bounded image-space chroma/luminance cleanup, not a generative edit.
    denoised=cv2.fastNlMeansDenoisingColored(cv2.cvtColor(srgb,cv2.COLOR_RGB2BGR),None,3,3,7,21)
    Image.fromarray(cv2.cvtColor(denoised,cv2.COLOR_BGR2RGB)).save(dest)
    np.save(SOURCE/(name+suffix+'-linear.npy'),output)
    rec={'scene':name,'seconds':round(time.monotonic()-started,2),'width':w,'height':h,'samples':passes*8,'engine':'Mitsuba '+mi.__version__+' / LLVM CPU path tracer','geometry_authoring':'Blender 5.2.2 LTS procedural meshes; Cycles not used in final','threads':3,'seed':71426,'file':str(dest),'denoising':'OpenCV non-local means, h=3, hColor=3, template=7, search=21; non-generative image-space cleanup','tone_map':'ACES-like filmic curve, explicit sRGB encoding','tile_size':tile}
    (SOURCE/(name+suffix+'-render.json')).write_text(json.dumps(rec,indent=2)+'\n')
    print('RENDER_COMPLETED',json.dumps(rec),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scene',default='all');p.add_argument('--samples',type=int,default=64);p.add_argument('--scale',type=float,default=1)
    a=p.parse_args();textures()
    for name in ['hero-glasshouse','sky-study','skin-ritual','quiet-growth'] if a.scene=='all' else [a.scene]:render(name,a.samples,a.scale)
