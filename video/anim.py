import os,sys,math,bpy,mathutils
from mathutils import Vector
B='/workspace/truedge-shop/renders_v1.22/build/'
src=open(B+'render_main_v122_alb.py').read().replace("bpy.ops.render.render(write_still=True)","")
exec(src)
SHOT=os.environ['SHOT']; W,H=map(int,os.environ['RES'].split('x'))
r.resolution_x=W; r.resolution_y=H; r.resolution_percentage=100
sc.cycles.samples=int(os.environ.get('SPP','24')); sc.cycles.adaptive_threshold=0.01; sc.cycles.denoising_prefilter='ACCURATE'; sc.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'; sc.cycles.filter_width=1.8
sc.cycles.seed=0; sc.cycles.use_animated_seed=False
sc.render.fps=30; r.image_settings.file_format='PNG'
vert=H>W
c15,s15=math.cos(math.radians(15)),math.sin(math.radians(15))
def P(u,s,z): return Vector((c15*u-s15*s, s15*u+c15*s, z))*0.001
cd.sensor_fit='HORIZONTAL'; cd.sensor_width=36
emp=bpy.data.objects.new("tgt",None); sc.collection.objects.link(emp)
cam.constraints.clear(); tc_=cam.constraints.new('TRACK_TO'); tc_.target=emp; tc_.track_axis='TRACK_NEGATIVE_Z'; tc_.up_axis='UP_Y'
cam.rotation_euler=(0,0,0); cd.dof.focus_object=emp
def key(f,loc,tgt,lens,focus=None,fstop=None):
    cam.location=loc; emp.location=tgt; cd.lens=lens
    if fstop: cd.dof.aperture_fstop=fstop
    cam.keyframe_insert('location',frame=f); emp.keyframe_insert('location',frame=f)
    cd.keyframe_insert('lens',frame=f); cd.dof.keyframe_insert('aperture_fstop',frame=f)
def ease_all():
    for idb in (cam,cd,emp):
        ad=idb.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                for k in fc.keyframe_points: k.interpolation='BEZIER'; k.easing='AUTO'
# sweeping rim light (all shots get extra edge rim for black)
l=bpy.data.lights.new("sweep",'AREA'); l.shape='RECTANGLE'; l.size=0.25; l.size_y=0.02; l.energy=float(os.environ.get('SW','6')); l.spread=math.radians(25)
so=bpy.data.objects.new("sweep",l); sc.collection.objects.link(so)
so.light_linking.receiver_collection=bpy.data.collections['rx_body']
def lkey(f,loc,tgt=Vector((0,0,0.008))):
    so.location=loc; so.rotation_euler=(tgt-so.location).to_track_quat('-Z','Y').to_euler()
    so.keyframe_insert('location',frame=f); so.keyframe_insert('rotation_euler',frame=f)
sc.objects['key'].data.energy*=float(os.environ.get('KEYK','1'))
fs=1
if SHOT=='1':
    fe=113
    d=Vector((0.2,-0.85,0.9)).normalized()
    D=0.15
    t0=P(-30,0,14); t1=P(26,0,14)
    LN=100
    key(fs,t0+d*D,t0,LN,fstop=5.6); key(fe,t1+d*D,t1,LN,fstop=5.6)
    lkey(fs,Vector((-0.30,0.10,0.06))); lkey(fe,Vector((0.30,0.15,0.06)))
elif SHOT=='2':
    fe=128; tgt=Vector((0.0,0,0.006))
    # smooth orbit: set every frame from a smoothstep-eased angle (no mid keys -> no velocity bumps)
    for f in range(fs,fe+1):
        t=(f-fs)/(fe-fs); t=t*t*(3-2*t); a=math.radians(-150+110*t); R=0.40
        key(f,tgt+Vector((math.cos(a)*R,math.sin(a)*R,0.17)),tgt,(100 if vert else 55),fstop=8)
    for kl in (so,):
        lkey(fs,Vector((-0.25,0.30,0.08))); lkey(fe,Vector((0.20,0.35,0.06)))
    # key light orbits slightly to reveal
    kk=sc.objects['key']
    for f,x in ((fs,-0.25),(fe,0.05)):
        kk.location=Vector((x,0.02,0.40)); kk.rotation_euler=(Vector((0,0,0.009))-kk.location).to_track_quat('-Z','Y').to_euler()
        kk.keyframe_insert('location',frame=f); kk.keyframe_insert('rotation_euler',frame=f)
else:
    fe=120
    tgt=Vector((0.004,0.0,0.007)); dirv=Vector((1.0,-0.62,0.52)).normalized()
    Dh=0.50
    key(fs,tgt+dirv*Dh*0.55+Vector((0,0,-0.02)),tgt+Vector((0.01,0,0)),(110 if vert else 60),fstop=5)
    key(90,tgt+dirv*Dh,tgt,(110 if vert else 60),fstop=10)
    key(fe,tgt+dirv*Dh,tgt,(110 if vert else 60),fstop=10)
    lkey(fs,Vector((-0.30,0.30,0.05))); lkey(90,Vector((-0.30,0.35,0.10))); lkey(fe,Vector((-0.30,0.35,0.10)))
ease_all()
if SHOT=='2':
    for fc in cam.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation='LINEAR'
for o in ('key','fill','rim'):
    if o in sc.objects and sc.objects[o].type=='LIGHT': sc.objects[o].data.energy*=float(os.environ.get('LK','1.4'))
sc.view_settings.exposure=float(os.environ.get('EXPO','-1.6'))
# make held frames truly static
sc.frame_start=int(os.environ.get('FS',fs)); sc.frame_end=int(os.environ.get('FE',fe)); sc.frame_step=int(os.environ.get('STEP','1'))
r.filepath=os.environ['OUT']+'/f_'
bpy.ops.render.render(animation=True)
