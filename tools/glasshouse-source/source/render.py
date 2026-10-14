"""Original DAYLIGHT GLASSHOUSE still lifes. No external geometry/textures.
Run from the asset root with isolated uv; see SUMMARY.md. Deterministic seed 71426.
Provenance: authored procedural geometry, Blender Cycles CPU; not AI photographs.
"""
import argparse
import json
import math
import os
from pathlib import Path
import random
import time

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'source'
SEED = 71426
random.seed(SEED)
PI = math.pi


def rgb(h):
    vals = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in vals) + (1,)


def material(name, color, rough=.4, transmission=0, metal=0, noise=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = rgb(color)
    m.use_nodes = True
    n = m.node_tree.nodes
    l = m.node_tree.links
    bs = n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = rgb(color)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Transmission Weight'].default_value = transmission
    bs.inputs['IOR'].default_value = 1.46
    if noise:
        tex = n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 65 if 'mineral' in name else 90
        tex.inputs['Detail'].default_value = 3
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .24
        bump.inputs['Distance'].default_value = noise
        l.new(tex.outputs['Fac'], bump.inputs['Height'])
        l.new(bump.outputs['Normal'], bs.inputs['Normal'])
        ramp = n.new('ShaderNodeValToRGB')
        c = rgb(color)
        ramp.color_ramp.elements[0].position = .17
        ramp.color_ramp.elements[0].color = tuple(v*.75 for v in c[:3])+(1,)
        ramp.color_ramp.elements[1].position = .84
        ramp.color_ramp.elements[1].color = c
        l.new(tex.outputs['Fac'], ramp.inputs['Fac'])
        l.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    return m


def assign(obj, mat):
    obj.data.materials.append(mat)
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def mesh(name, verts, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return assign(obj, mat)


def curve(name, pts, radius, mat):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 3
    data.bevel_depth = radius
    data.bevel_resolution = 1
    s = data.splines.new('BEZIER')
    s.bezier_points.add(len(pts)-1)
    for b, p in zip(s.bezier_points, pts):
        b.co = p
        b.handle_left_type = 'AUTO'
        b.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    return assign(o, mat)


def cube(name, loc, scale, mat, bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, mat)
    if bevel:
        mod = o.modifiers.new('soft mineral edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 4
        o.modifiers.new('weighted normals', 'WEIGHTED_NORMAL')
    return o


def sphere(name, pos, radius, mat, scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=48, radius=radius, location=pos)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    return assign(o, mat)


def lathe(name, profile, loc, mat, rib=0, count=128):
    verts, faces = [], []
    for r,z in profile:
        for i in range(count):
            a = 2*PI*i/count
            rr = r + rib * math.cos(a*32) * min(1, r*5)
            verts.append((loc[0]+rr*math.cos(a), loc[1]+rr*math.sin(a), loc[2]+z))
    for j in range(len(profile)-1):
        for i in range(count):
            ni = (i+1)%count
            faces.append((j*count+i,j*count+ni,(j+1)*count+ni,(j+1)*count+i))
    o = mesh(name, verts, faces, mat)
    sub = o.modifiers.new('porcelain soft profile', 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    return o


def cylinder(name, xy, r, z, h, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=r, depth=h, location=(xy[0],xy[1],z+h/2))
    o = bpy.context.object
    o.name = name
    assign(o, mat)
    b = o.modifiers.new('honed edges', 'BEVEL')
    b.width = min(.055,h/4)
    b.segments = 4
    o.modifiers.new('weighted normals', 'WEIGHTED_NORMAL')
    return o


def leaf(name, start, end, width, mat, bend=.13, veins=True, facing=(0,-.65,1)):
    """Actual curved botanical lamina mesh, petiole, midrib and lateral veins."""
    a, b = Vector(start), Vector(end)
    direction = b-a
    length = direction.length
    axis = direction.normalized()
    normal = Vector(facing)
    side = axis.cross(normal).normalized()
    if side.length < .1:
        side = axis.cross(Vector((1,0,0))).normalized()
    normal = side.cross(axis).normalized()
    def point(t, s):
        envelope = math.sin(PI*t)**.78
        w = width * envelope * (.95+.05*math.sin(t*27))
        center = a+direction*t + normal*(bend*length*math.sin(PI*t))
        # Raised central fold, asymmetrical rolled margin, lightly ruffled edge.
        p = center + side*(s*w/2)
        p += normal*(-abs(s)**1.4*w*.15 + s*s*.018*math.sin(t*36))
        p += side*(.055*width*math.sin(t*PI))
        return p
    rows, cols = 22, 8
    verts = [tuple(point(i/rows, -1+2*j/cols)) for i in range(rows+1) for j in range(cols+1)]
    faces = []
    for i in range(rows):
        for j in range(cols):
            k = i*(cols+1)+j
            faces.append((k,k+1,k+cols+2,k+cols+1))
    o = mesh(name, verts, faces, mat)
    solid = o.modifiers.new('living leaf thickness', 'SOLIDIFY')
    solid.thickness = .003
    if veins:
        lift = normal*.0035
        curve(name+' midrib', [point(t,0)+lift for t in (0,.15,.3,.5,.7,.88,1)], .0045, M['vein'])
        for i in range(1,10):
            t = i/11
            for sign in (-1,1):
                curve(name+' side vein', [point(t,0)+lift, point(t+.025,sign*.45)+lift, point(min(.98,t+.06),sign*.92)+lift], .0017, M['vein'])
    return o


def branch(base, tip, width=.6, pairs=5, name='laurel'):
    a,b = Vector(base),Vector(tip)
    d = b-a
    def stem(t):
        return a+d*t+Vector((math.sin(PI*t)*.12,math.sin(PI*t)*.12,math.sin(PI*t)*.15))
    curve(name+' stem', [stem(t) for t in (0,.2,.4,.6,.8,1)], .017, M['stem'])
    for i in range(pairs):
        t = .24+.65*i/pairs
        p = stem(t)
        for sign in (-1,1):
            end = p+Vector((sign*width*(.85+random.random()*.45),-.1-random.random()*.26,.25+random.random()*.35))
            petiole = p+(end-p)*.15
            curve(name+' petiole', [p,petiole], .008, M['stem'])
            leaf(name+' leaf',petiole,end,width*.46,random.choice(M['leaves']),bend=random.uniform(.08,.2))
    leaf(name+' tip', stem(.89), b+Vector((.12,-.13,.35)),width*.24, M['leaves'][1])


def fern(base, tip, spread=.58):
    a,b = Vector(base),Vector(tip)
    def stem(t):
        return a+(b-a)*t + Vector((0,-.15*math.sin(PI*t),.25*math.sin(PI*t)))
    curve('fern arching rachis',[stem(t) for t in (0,.2,.4,.6,.8,1)],.012,M['stem'])
    for i in range(25):
        t = .12+i*.033
        p = stem(t)
        breadth = spread*math.sin(PI*t)**.8
        for sign in (-1,1):
            e = p+Vector((sign*breadth,-.05,.12+.09*(1-t)))
            leaf('fern pinna',p,e,.09*(1-.55*t),M['leaves'][i%3],bend=.1,veins=False)


def arc_wall(center=(-1,1.8), radius=2.7, height=3.5, start=.12, end=2.75):
    verts, faces = [], []
    for z in (0,height):
        for r in (radius,radius+.18):
            for i in range(81):
                a=start+(end-start)*i/80
                verts.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),z))
    n=81
    for i in range(80):
        faces.extend([(i,i+1,2*n+i+1,2*n+i),(n+i,3*n+i,3*n+i+1,n+i+1),(2*n+i,2*n+i+1,3*n+i+1,3*n+i),(i,n+i,n+i+1,i+1)])
    faces.extend([(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)])
    o=mesh('jade architectural curved screen',verts,faces,M['jade'])
    b=o.modifiers.new('cast edge softness','BEVEL'); b.width=.055; b.segments=3
    o.modifiers.new('architectural normals','WEIGHTED_NORMAL')
    return o


def amber_arc(pos,r=1.15):
    # Solid curved glass ribbon; not a drawn orbit line.
    verts,faces=[],[]
    for i in range(97):
        a=-.25+PI*1.23*i/96
        for rad,dy in ((r-.15,-.14),(r+.15,-.14),(r+.15,.14),(r-.15,.14)):
            verts.append((pos[0]+rad*math.cos(a),pos[1]+dy,pos[2]+rad*math.sin(a)))
    for i in range(96):
        for j in range(4):
            faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    faces.extend([(3,2,1,0),(384,385,386,387)])
    o=mesh('cast amber glass crescent',verts,faces,M['amber'])
    mod=o.modifiers.new('fire polished edges','BEVEL');mod.width=.055;mod.segments=4
    o.modifiers.new('glass normals','WEIGHTED_NORMAL')


def light(name,loc,target,power,size,color,shape='DISK',size_y=None):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power;data.shape=shape;data.size=size;data.color=color
    if size_y is not None:data.size_y=size_y
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()


def setup(name, width, height, samples):
    global M
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(SEED+['hero-glasshouse','sky-study','skin-ritual','quiet-growth'].index(name))
    M={
        'floor':material('cool pale jade plaster','E6EDE3',.58,noise=.018),
        'jade':material('cast pale jade architectural mineral','B7CDB9',.52,noise=.014),
        'stone':material('honed calcite mineral','D5DCCC',.47,noise=.025),
        'moon':material('celestial chalk mineral','CAD3C5',.66,noise=.055),
        'ceramic':material('spruce satin ceramic','183F35',.26,noise=.006),
        'ivory':material('cool porcelain','D8E4D7',.27,noise=.007),
        'amber':material('honey amber cast glass','D9AE58',.095,transmission=1),
        'frost':material('frosted pale jade glass','E6EDE3',.25,transmission=.92,noise=.005),
        'water':material('clear water','DBEEE4',.055,transmission=1),
        'stem':material('living green stem','395632',.42),
        'vein':material('subtle pale leaf rib','648145',.43),
        'leaves':[material('waxed leaf '+str(i),c,.28+i*.035,noise=.004) for i,c in enumerate(('254E28','3C642E','527A38','173E2E'))]
    }
    M['water'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.333
    for m in M['leaves']:
        bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Subsurface Weight'].default_value=.045
        bs.inputs['Coat Weight'].default_value=.22;bs.inputs['Coat Roughness'].default_value=.32
    # Tinted glass uses a very weak physical absorption, no artificial glow.
    n=M['amber'].node_tree.nodes;l=M['amber'].node_tree.links
    vol=n.new('ShaderNodeVolumeAbsorption');vol.inputs['Color'].default_value=rgb('D6A850');vol.inputs['Density'].default_value=.13
    l.new(vol.outputs['Volume'],n.get('Material Output').inputs['Volume'])
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=samples
    scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.035
    scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8
    scene.render.threads_mode='FIXED';scene.render.threads=3
    scene.render.use_persistent_data=False
    scene.cycles.use_auto_tile=True;scene.cycles.tile_size=256
    scene.render.use_simplify=True;scene.render.simplify_subdivision_render=1
    scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
    scene.render.film_transparent=False
    scene.world=bpy.data.worlds.new('soft cool daylight');scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.63,.75,.67,1);bg.inputs['Strength'].default_value=.38
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=.45
    cube('infinite pale jade floor',(0,0,-.13),(200,200,.25),M['floor'],0)
    light('large sunlit window',(-3.8,-4.0,7.4),(0,0,.5),1400,3.4,(1,.91,.73),'RECTANGLE',4.5)
    light('cool glasshouse fill',(4,-1,5),(0,0,1),420,5,(.76,.9,1))
    light('rear glass edge',(1.5,4.0,6),(0,0,1),950,3,(1,.96,.84))
    # Off-camera window mullions intercept the key light for soft architectural shadows.
    for x in (-4.2,-3.0,-1.8):
        cube('window shadow mullion',(x,-2,4.2),(.07,.1,3),M['ceramic'],.015)
    cube('window shadow transom',(-3,-2,4.6),(4,.1,.08),M['ceramic'],.01)
    bpy.ops.object.camera_add(location=(5,-12,6.5))
    cam=bpy.context.object;cam.name='editorial still life camera';scene.camera=cam
    cam.data.type='ORTHO';cam.data.ortho_scale=8.8
    target=Vector((0,.3,1.5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    return scene,cam


def hero():
    arc_wall(center=(-1,1.0),radius=2.8,height=3.65,start=.36,end=2.95)
    cylinder('large floating mineral stage',(-.5,0),1.55,.015,.33,M['stone'])
    cylinder('amber orb mineral column',(-.7,.1),.68,.345,.47,M['stone'])
    sphere('sunlike amber glass orb',(-.7,.1,1.66),.84,M['amber'])
    lathe('shallow ceramic water dish',[(0,0),(.95,0),(1.1,.05),(1.13,.13),(1.11,.18),(1.06,.18),(1.03,.11),(.88,.075),(0,.075)],(1.25,-.8,.015),M['jade'])
    cylinder('still water in dish',(1.25,-.8),1.025,.095,.025,M['water'])
    lathe('botanical low vessel',[(0,0),(.42,0),(.52,.12),(.54,.4),(.45,.64),(.35,.69),(.3,.69),(.32,.61),(.4,.38),(.34,.12),(0,.12)],(1.15,.95,0),M['ceramic'],rib=.009)
    for tip,w,p in [((2.2,1.15,3.25),.85,5),((.95,1.3,3.65),.8,5),((2.7,.65,2.6),.85,5),((.5,1.25,2.85),.65,4)]:
        branch((1.15,.95,.55),tip,w,p)
    fern((1.1,.9,.6),(2.8,-.05,1.3),.5)
    fern((1.1,1,.6),(.6,-.5,2.5),.55)
    leaf('foreground large resting leaf',(-1.75,-1.3,.065),(-.1,-1.8,.12),.62,M['leaves'][1],bend=.2)


def sky():
    arc_wall(center=(-1,1.8),radius=2.6,height=3.8,start=.35,end=2.9)
    cube('monolithic chalk platform',(.35,.3,.25),(2.25,1.75,.5),M['stone'],.08)
    sphere('sculptural celestial mineral sphere',(.25,.35,1.61),1.1,M['moon'])
    # Additional low-frequency mineral structure is generated in shader, not photo texture.
    mat=M['moon'];n=mat.node_tree.nodes;l=mat.node_tree.links
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=5;noise.inputs['Roughness'].default_value=.75
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.23;ramp.color_ramp.elements[0].color=rgb('96AA98');ramp.color_ramp.elements[1].position=.74;ramp.color_ramp.elements[1].color=rgb('DCE2D6')
    l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
    amber_arc((1.4,.65,1.32),1.08)
    lathe('low stem vessel',[(0,0),(.4,0),(.42,.15),(.34,.36),(.2,.42),(.16,.42),(.2,.12),(0,.1)],(-1.65,.65,0),M['ceramic'])
    branch((-1.65,.65,.3),(-1.7,1,2.9),.72,5)
    branch((-1.65,.65,.3),(-2.4,.2,1.9),.62,4)
    fern((-1.65,.65,.3),(-.75,-.5,1.0),.45)
    cylinder('foreground amber lens',(1.05,-1.15),.49,.025,.12,M['amber'])


def skin():
    arc_wall(center=(-1,1.5),radius=2.8,height=3.0,start=.4,end=2.85)
    cube('honed ritual tray',(0,.15,.17),(3.8,2.65,.34),M['stone'],.1)
    lathe('unbranded hollow frosted vessel',[(0,0),(.43,0),(.51,.08),(.53,.2),(.53,1.55),(.51,1.65),(.47,1.68),(.43,1.65),(.43,.22),(.37,.14),(0,.14)],(-.85,.6,.35),M['frost'],rib=.005)
    cylinder('water inside frosted vessel',(-.85,.6),.425,.49,1.16,M['water'])
    lathe('hand thrown shallow ritual bowl',[(0,0),(.42,0),(.6,.06),(.8,.19),(.98,.45),(1.01,.55),(.98,.58),(.94,.55),(.87,.41),(.69,.23),(.49,.14),(0,.14)],(.65,-.35,.35),M['ivory'])
    cylinder('quiet water in ritual bowl',(.65,-.35),.89,.35+.4,.025,M['water'])
    # Folded broad leaves emerge from a fine stem, not a graphic silhouette.
    curve('broad botanical petiole',[(1.25,1,.35),(1.6,.65,.65),(1.5,.1,1.05)],.019,M['stem'])
    leaf('large tactile ritual leaf',(1.5,.1,1.05),(.1,-1.4,1.22),1.05,M['leaves'][0],bend=.16)
    leaf('upright companion leaf',(1.55,.8,.58),(2.1,.75,2.42),.84,M['leaves'][1],bend=.16)
    cylinder('amber glass ritual disk',(-1.1,-.9),.37,.35,.105,M['amber'])
    for p,r in [((.5,-.67,1.17),.035),((.62,-.64,1.19),.025),((.77,-.54,1.21),.042)]:
        sphere('small water droplet on leaf',p,r,M['water'],(1,1,.6))


def growth():
    arc_wall(center=(-1,1.7),radius=2.8,height=3.5,start=.4,end=2.85)
    cylinder('low quiet growth plinth',(-.65,.3),1.27,.015,.22,M['stone'])
    lathe('ribbed spruce botanical vase',[(0,0),(.38,0),(.6,.15),(.7,.55),(.65,.95),(.49,1.31),(.27,1.5),(.25,1.66),(.21,1.69),(.17,1.65),(.19,1.48),(.39,1.25),(.55,.9),(.58,.5),(.44,.17),(0,.13)],(-.65,.3,.245),M['ceramic'],rib=.013)
    base=(-.65,.3,1.72)
    for tip,w,p in [((-1.7,.7,3.65),.78,5),((-.55,.7,4.1),.7,5),((.6,.6,3.6),.78,5),((1.3,.25,2.8),.7,4),((-2,.2,2.8),.65,4)]:
        branch(base,tip,w,p,name='growth laurel')
    lathe('outer nesting porcelain bowl',[(0,0),(.35,0),(.58,.1),(.85,.47),(.87,.58),(.83,.6),(.78,.52),(.5,.2),(.31,.12),(0,.12)],(1.15,-.55,.015),M['ivory'])
    lathe('inner nesting jade bowl',[(0,0),(.2,0),(.35,.09),(.53,.35),(.55,.41),(.51,.43),(.47,.34),(.28,.14),(0,.1)],(1.15,-.55,.15),M['jade'])
    lathe('smallest amber nesting vessel',[(0,0),(.13,0),(.23,.08),(.3,.27),(.28,.3),(.24,.27),(.18,.12),(0,.08)],(1.15,-.55,.28),M['amber'])
    leaf('fallen laurel resting on stone',(-1.5,-1.05,.05),(-.4,-1.4,.08),.4,M['leaves'][2],bend=.12)


SCENES={'hero-glasshouse':hero,'sky-study':sky,'skin-ritual':skin,'quiet-growth':growth}


def main():
    p=argparse.ArgumentParser();p.add_argument('--scene',choices=['all',*SCENES],default='all');p.add_argument('--samples',type=int,default=48);p.add_argument('--scale',type=float,default=1);p.add_argument('--save-blend',action='store_true')
    args=p.parse_args()
    records=[]
    for name in SCENES if args.scene=='all' else [args.scene]:
        width,height=(1800,1200) if name=='hero-glasshouse' else (1400,1050)
        scene,cam=setup(name,round(width*args.scale),round(height*args.scale),args.samples)
        SCENES[name]()
        if name=='hero-glasshouse':
            cam.data.ortho_scale=8.4
            target=Vector((.1,.45,1.6))
        elif name=='quiet-growth':
            cam.location=(4,-12,6.5);cam.data.ortho_scale=7.8;target=Vector((-.2,.35,1.9))
        elif name=='skin-ritual':
            cam.location=(4.8,-11,8);cam.data.ortho_scale=6.8;target=Vector((0,.25,1.1))
        else:
            cam.location=(4,-12,6.5);cam.data.ortho_scale=7.6;target=Vector((0,.35,1.45))
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        scene['origin']='Original authored procedural Blender illustration; not a photograph or image-model generation.'
        scene['brief']=(SOURCE/'ORIGIN.md').read_text()
        scene['seed']=SEED
        suffix='' if args.scale==1 else '-preview'
        scene.render.filepath=str(SOURCE/(name+suffix+'.png'))
        if args.save_blend:bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(name+'.blend')))
        start=time.monotonic()
        bpy.ops.render.render(write_still=True)
        rec={'scene':name,'seconds':round(time.monotonic()-start,2),'width':scene.render.resolution_x,'height':scene.render.resolution_y,'samples':args.samples,'engine':'Blender '+bpy.app.version_string+' / Cycles CPU','threads':3,'objects':len(scene.objects),'seed':SEED,'file':scene.render.filepath}
        records.append(rec)
        (SOURCE/(name+suffix+'-render.json')).write_text(json.dumps(rec,indent=2)+'\n')
        print('RENDER_COMPLETED '+json.dumps(rec),flush=True)
    print('ALL_REQUESTED_RENDERS_COMPLETE',flush=True)


if __name__=='__main__':
    main()
