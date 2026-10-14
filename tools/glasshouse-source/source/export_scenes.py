"""Export original authored Blender geometry to low-memory Mitsuba PLY scenes.
Blender is used only as mesh authoring/evaluation here, never as the renderer.
"""
import json
import math
from pathlib import Path
import struct
import sys
import bpy
from mathutils import Vector
import render as art

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'source'/'geometry'
OUT.mkdir(exist_ok=True)


def export(name):
    w,h=(1800,1200) if name=='hero-glasshouse' else (1400,1050)
    scene,cam=art.setup(name,w,h,48)
    art.SCENES[name]()
    if name=='hero-glasshouse':
        cam.data.ortho_scale=8.4;target=Vector((.1,.45,1.6))
    elif name=='quiet-growth':
        cam.location=(4,-12,6.5);cam.data.ortho_scale=7.8;target=Vector((-.2,.35,1.9))
    elif name=='skin-ritual':
        cam.location=(4.8,-11,8);cam.data.ortho_scale=6.8;target=Vector((0,.25,1.1))
    else:
        cam.location=(4,-12,6.5);cam.data.ortho_scale=7.6;target=Vector((0,.35,1.45))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    # Keep the source scene complete; off-camera mullions are not exported as visible props.
    for o in scene.objects:
        if 'window shadow' in o.name:o.hide_render=True
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/(name+'.blend')))
    deps=bpy.context.evaluated_depsgraph_get()
    groups={}
    for obj in list(scene.objects):
        if obj.type not in ('MESH','CURVE') or obj.hide_render:continue
        ev=obj.evaluated_get(deps)
        m=ev.to_mesh()
        if not m or not len(m.vertices):continue
        m.calc_loop_triangles()
        mat=obj.data.materials[0]
        key=mat.name
        g=groups.setdefault(key,{'vertices':[],'faces':[],'material':mat})
        offset=len(g['vertices'])
        normalmat=obj.matrix_world.to_3x3().inverted().transposed()
        for v in m.vertices:
            p=obj.matrix_world@v.co;n=(normalmat@v.normal).normalized()
            # Parametric mapping for authored procedural textures, not external photographs.
            if 'sphere' in obj.name or 'orb' in obj.name:
                q=v.co.normalized();u=math.atan2(q.y,q.x)/(2*math.pi)+.5;vv=math.asin(max(-1,min(1,q.z)))/math.pi+.5
            else:
                u=float(p.x*.55+p.y*.23);vv=float(p.z*.55+p.y*.3)
            g['vertices'].append((*p,*n,u,vv))
        g['faces'].extend(tuple(offset+i for i in tri.vertices) for tri in m.loop_triangles)
        ev.to_mesh_clear()
    manifests=[]
    for idx,(key,g) in enumerate(groups.items()):
        path=OUT/(name+'-'+str(idx)+'.ply')
        with path.open('wb') as f:
            f.write(('ply\nformat binary_little_endian 1.0\nelement vertex '+str(len(g['vertices']))+'\nproperty float x\nproperty float y\nproperty float z\nproperty float nx\nproperty float ny\nproperty float nz\nproperty float s\nproperty float t\nelement face '+str(len(g['faces']))+'\nproperty list uchar int vertex_indices\nend_header\n').encode())
            for v in g['vertices']:f.write(struct.pack('<8f',*v))
            for face in g['faces']:f.write(struct.pack('<B3i',3,*face))
        bs=g['material'].node_tree.nodes.get('Principled BSDF')
        manifests.append({'name':key,'ply':str(path.relative_to(ROOT)),'vertices':len(g['vertices']),'triangles':len(g['faces']),'color':list(bs.inputs['Base Color'].default_value[:3]),'roughness':bs.inputs['Roughness'].default_value,'transmission':bs.inputs['Transmission Weight'].default_value,'ior':bs.inputs['IOR'].default_value})
    result={'name':name,'width':w,'height':h,'camera':{'origin':list(cam.location),'target':list(target),'scale':cam.data.ortho_scale},'geometry':manifests,'seed':art.SEED}
    (ROOT/'source'/(name+'-scene.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('EXPORTED',name,'groups',len(groups),'triangles',sum(x['triangles'] for x in manifests),flush=True)


if __name__=='__main__':
    for name in sys.argv[1:] or art.SCENES:export(name)
