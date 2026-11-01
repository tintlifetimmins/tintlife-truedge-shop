# TruEdge display GLBs: body (material 0, untouched) + hardware nodes, all toggled by the "Blades" button.
# Sources (model frame, mm): blade = truedge-mini/work/blade_true_placed.stl seated position;
# holes/pockets measured from truedge-mini/ref_truedge_v1.22_body.stl (full) and work17/model_frame.stl (Mini);
# CLAMP/SP/spare-hole coordinates from truedge-mini/truedge_mini_v1.7.scad.
import trimesh,numpy as np,json,struct,re,shapely.geometry as sg,shapely.affinity as sa,manifold3d as mf
SCAD=open('/workspace/truedge-mini/truedge_mini_v1.7.scad').read()
SP=sg.Polygon(eval(re.search(r'SP = (\[\[.*?\]\]);',SCAD).group(1)))
CLAMP=[(-28.205,-2.911),(25.885,11.581)];SPH=(5.227,-25.352)  # bore centres fitted (largest inscribed circle) from the v1.22 body; scad values (-28.20,-2.91),(25.88,11.58),(5.23,-25.2)
E0=np.array([-29.457,-6.722,11.217]);E1=np.array([28.83,8.906,11.216]);B0=np.array([-20.42,13.489,14.36]);B1=np.array([10.949,21.928,14.364])
u=(E1-E0)/np.linalg.norm(E1-E0);v=B0-E0;v-=u*(v@u);v/=np.linalg.norm(v);n=np.cross(u,v)
if n[2]<0:n=-n
T=0.65*n[2];uv=lambda p:((p-E0)@u,(p-E0)@v)
e0,e1,b0,b1=[uv(p) for p in (E0,E1,B0,B1)]
def outline():
  o=sg.Polygon([e0,e1,b1,b0]);bm=((b0[0]+b1[0])/2,b0[1])
  for dx in (-8.5,8.5):o=o.difference(sg.Point(bm[0]+dx,bm[1]).buffer(1.7,16))
  return o
OL=outline()
M=np.eye(4);M[:3,0]=u;M[:3,1]=v;M[:3,2]=n;M[:3,3]=E0
# working blade: clearance arcs where the clamp-screw shanks pass the blade ends (see report)
wb=OL
for c in CLAMP:
  cc=np.array([c[0],c[1],12.0]);pu,pv=(cc-E0)@u,(cc-E0)@v  # projected (vertical shank ~ plane normal within 10 deg)
  wb=wb.difference(sg.Point(pu,pv).buffer(1.85,24))
WB=trimesh.creation.extrude_polygon(wb,T);WB.apply_transform(M)
# spare blade: flat (z up) on spare-pocket floor z=13.6, cutting edge parallel to pocket's long edge
sp_e0=np.array([-31.08,-12.983]);sp_e1=np.array([30.478,3.512]);ang=np.arctan2(*(sp_e1-sp_e0)[::-1])
base=sa.translate(OL,-e0[0],-e0[1])               # edge-left at origin, edge along +x, back toward +y
base=sa.scale(base,1,-1,origin=(0,0))               # back toward -y (pocket back is below its edge line)
best=None;shank=sg.Point(SPH).buffer(1.6,24);inner=SP.buffer(-0.08)
for s in np.arange(0,4.01,0.05):
  for w in np.arange(0.1,3.01,0.05):
    g=sa.rotate(sa.translate(base,s,-w),ang,origin=(0,0),use_radians=True);g=sa.translate(g,*sp_e0)
    if inner.contains(g) and not g.intersects(shank):
      m=min(g.exterior.distance(sg.Point(SPH)),1e9);sc=-abs(s-2)-w
      if best is None or sc>best[0]:best=(sc,g,s,w)
assert best,'spare does not fit';SPG=best[1];print('spare blade offset along edge %.2f, inset %.2f'%(best[2],best[3]))
SB=trimesh.creation.extrude_polygon(SPG,T);SB.apply_translation([0,0,13.6+0.005])
def revolve(prof,seg=20):return trimesh.creation.revolve(np.array(prof),sections=seg)
def screw(x,y,zb,shank_d,L=8.0):
  # ISO 7380 M3 button head (dk 5.7, k 1.65) with 2 mm hex socket, shank shown plain
  dk,k=5.7,1.65
  prof=[[0,-L],[shank_d/2,-L],[shank_d/2,0],[dk/2,0],[dk/2,0.35],[dk/2-0.6,1.25],[1.6,k],[0,k]]
  h=revolve(prof);hx=trimesh.creation.cylinder(radius=1.0/np.cos(np.pi/6)*1.0,height=2.0,sections=6);hx.apply_translation([0,0,k])
  h=mfd(h)-mfd(hx);h=tm(h);h.apply_translation([x,y,zb]);return h
from shapely.ops import polylabel,unary_union
def bore_fit(body,x,y,z0,z1):
  # largest circle inside the bore over z0..z1 (intersection of slices)
  P=None
  for z in np.linspace(z0+0.05,z1-0.05,8):
    s=body.section(plane_origin=[0,0,z],plane_normal=[0,0,1]);best=None
    for e in s.discrete:
      pg=sg.Polygon(e[:,:2])
      if pg.is_valid and pg.contains(sg.Point(x,y)) and pg.area<60:best=pg if best is None or pg.area<best.area else best
    P=best if P is None else P.intersection(best)
  c=polylabel(P,0.001);return c.x,c.y,P.exterior.distance(c)
def insert(x,y,z0,L,od,idd=3.0):
  t=trimesh.creation.annulus(r_min=idd/2,r_max=od/2,height=L,sections=20);t.apply_translation([x,y,z0+L/2]);return t
mfd=lambda m:mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
def tm(M):mm=M.to_mesh();return trimesh.Trimesh(mm.vert_properties[:,:3],mm.tri_verts)
def headz(body,parts,x,y,r=2.85):
  sc=trimesh.Scene([body]+parts);allm=trimesh.util.concatenate([body]+parts);z=0
  for a in np.linspace(0,2*np.pi,72,endpoint=False):
    for rr in (0,r*0.33,r*0.66,r):
      h=allm.ray.intersects_location([[x+rr*np.cos(a),y+rr*np.sin(a),17.3]],[[0,0,-1]])[0]
      if len(h):z=max(z,h[:,2].max())
  return z+0.03
R=np.array([[1,0,0],[0,0,-1],[0,1,0]],float)
def ov(a,b):return (mfd(a)^mfd(b)).volume()
out={}
for name,src,t,base_glb in [('full-v1.23','/workspace/truedge-mini/ref_truedge_v1.22_body.stl',[0,8.75,0],'base_full.glb'),('mini-v1.7','/workspace/truedge-mini/work17/model_frame.stl',[0,8.75,-7.555],'base_mini.glb')]:
  body=trimesh.load(src);parts={'blade':[WB]};info=[]
  if name.startswith('full'):
    parts['blade'].append(SB)
    ins=[]
    for (x,y),zt in [(CLAMP[0],11.0),(CLAMP[1],11.0),(SPH,13.25)]:
      cx,cy,r=bore_fit(body,x,y,zt-5.7,zt);print(name,'bore at',(x,y),'fit centre',(round(cx,3),round(cy,3)),'r %.3f'%r);ins.append(insert(cx,cy,zt-5.7,5.7,min(3.96,2*r-0.04)))
    parts['insert']=ins;shd=2.9
    holes=CLAMP+[SPH]
  else:
    parts['insert']=[];shd=2.46;holes=CLAMP
  scr=[]
  for (x,y) in holes:
    zb=headz(body,parts['blade'],x,y);s=screw(x,y,zb,shd);scr.append(s);info.append((x,y,round(zb,2),round(zb-8,2)))
  parts['screw']=scr
  allp=[p for k in parts for p in parts[k]]
  print(name,'screw head-bottom/tip z',info)
  print(name,'overlap with body mm3:',[round(ov(p,body),4) for p in allp])
  print(name,'screw vs blades/inserts:',[round(ov(s,b),4) for s in scr for b in parts['blade']+parts['insert']])
  # contact (not floating): min distance from each part to body / supporting part
  for k,p in [(k,p) for k in parts for p in parts[k]]:
    pts=trimesh.sample.sample_surface(p,1500,seed=3)[0];d=np.abs(trimesh.proximity.signed_distance(trimesh.util.concatenate([body]+parts['blade']),pts)).min() if k!='blade' else np.abs(trimesh.proximity.signed_distance(body,pts)).min()
    print('  ',name,k,'min gap to support %.3f mm'%d)
  # write glb
  d=open(base_glb,'rb').read();jl=struct.unpack('<I',d[12:16])[0];j=json.loads(d[20:20+jl]);bo=20+jl;bl=struct.unpack('<I',d[bo:bo+4])[0];bin_=bytearray(d[bo+8:bo+8+bl])
  for mm in j['meshes']:mm.pop('extras',None)
  def add(arr,comp,typ,target):
    while len(bin_)%4:bin_.append(0)
    off=len(bin_);by=arr.tobytes();bin_.extend(by);j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(by),'target':target})
    a={'bufferView':len(j['bufferViews'])-1,'componentType':comp,'count':arr.shape[0],'type':typ}
    if typ=='VEC3':a['min']=arr.min(0).tolist();a['max']=arr.max(0).tolist()
    j['accessors'].append(a);return len(j['accessors'])-1
  MAT={'blade':{'name':'blade_steel','pbrMetallicRoughness':{'baseColorFactor':[0.578,0.603,0.630,1],'metallicFactor':1.0,'roughnessFactor':0.35}},
       'insert':{'name':'insert_brass','pbrMetallicRoughness':{'baseColorFactor':[0.462,0.381,0.054,1],'metallicFactor':1.0,'roughnessFactor':0.35}},
       'screw':{'name':'screw_steel','pbrMetallicRoughness':{'baseColorFactor':[0.30,0.31,0.33,1],'metallicFactor':1.0,'roughnessFactor':0.4}}}
  for k in ('blade','insert','screw'):
    if not parts[k]:continue
    j['materials'].append(MAT[k]);mi=len(j['materials'])-1
    for i,p in enumerate(parts[k]):
      b=p.copy();b.vertices=(p.vertices@R.T+np.array(t))/1000.
      smooth=k!='blade'
      if smooth:
        b=trimesh.Trimesh(b.vertices,b.faces,process=True);V=b.vertices.astype(np.float32);N=trimesh.smoothing.get_vertices_normals(b) if False else b.vertex_normals.astype(np.float32);I=b.faces.reshape(-1).astype(np.uint16)
        # crisp normals on flat faces: split by face-angle
        V=b.vertices[b.faces].reshape(-1,3).astype(np.float32);fn=np.repeat(b.face_normals,3,0);vn=b.vertex_normals[b.faces].reshape(-1,3)
        N=np.where((np.sum(fn*vn,1)>0.9)[:,None],vn,fn).astype(np.float32);I=np.arange(len(V),dtype=np.uint16)
      else:
        V=b.vertices[b.faces].reshape(-1,3).astype(np.float32);N=np.repeat(b.face_normals,3,0).astype(np.float32);I=np.arange(len(V),dtype=np.uint16)
      ia=add(I,5123,'SCALAR',34963);pa=add(V,5126,'VEC3',34962);na=add(N,5126,'VEC3',34962)
      nm=k if k!='blade' else ('blade' if i==0 else 'blade_spare')
      if k!='blade':nm='%s_%d'%(k,i+1)
      j['meshes'].append({'name':nm,'primitives':[{'attributes':{'POSITION':pa,'NORMAL':na},'indices':ia,'mode':4,'material':mi}]})
      j['nodes'].append({'name':nm,'mesh':len(j['meshes'])-1});j['scenes'][0]['nodes'].append(len(j['nodes'])-1)
  while len(bin_)%4:bin_.append(0)
  j['buffers']=[{'byteLength':len(bin_)}];js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
  o=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(bin_))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(bin_),0x004E4942)+bytes(bin_)
  f='/workspace/truedge-colourtext/models/truedge-%s.glb'%name;open(f,'wb').write(o);print(name,'glb bytes',len(o))
