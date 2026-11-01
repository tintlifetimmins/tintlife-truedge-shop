# Build Stanley-1992-style blade (trapezoid + 2 back notches) at the real seated position
# (from truedge-mini/work/blade_true_placed.stl, model frame) and append it as a separate
# node/material "blade" to the display GLBs. Body primitive/material 0 untouched.
import trimesh,numpy as np,json,struct,shapely.geometry as sg
P=trimesh.load('/workspace/truedge-mini/work/blade_true_placed.stl').vertices
bot=sorted([p for p in P],key=lambda p:p[2])[:0]
low=P[np.argsort(P[:,2])]
E0=np.array([-29.457,-6.722,11.217]);E1=np.array([28.83,8.906,11.216])
B0=np.array([-20.42,13.489,14.36]);B1=np.array([10.949,21.928,14.364])
u=(E1-E0)/np.linalg.norm(E1-E0);v=B0-E0;v-=u*(v@u);v/=np.linalg.norm(v);n=np.cross(u,v)
if n[2]<0:n=-n
T=0.65*n[2]
uv=lambda p:((p-E0)@u,(p-E0)@v)
e0,e1,b0,b1=[uv(p) for p in (E0,E1,B0,B1)]
outline=sg.Polygon([e0,e1,b1,b0])
bm=((b0[0]+b1[0])/2,b0[1])
for dx in (-8.5,8.5):outline=outline.difference(sg.Point(bm[0]+dx,bm[1]).buffer(1.7,16))
m=trimesh.creation.extrude_polygon(outline,T)
M=np.eye(4);M[:3,0]=u;M[:3,1]=v;M[:3,2]=n;M[:3,3]=E0
m.apply_transform(M)
print('blade dims edge %.2f back %.2f height %.2f thick %.2f'%(np.hypot(*np.subtract(e1,e0)),np.hypot(*np.subtract(b1,b0)),b0[1],T),'tilt %.1f deg'%np.degrees(np.arccos(n[2])))
# model frame -> glb (registered, residual <0.02 mm)
R=np.array([[1,0,0],[0,0,-1],[0,1,0]],float)
import manifold3d as mf
def inter(a,b):
  A=mf.Manifold(mf.Mesh(np.asarray(a.vertices,np.float32),np.asarray(a.faces,np.uint32)));Bm=mf.Manifold(mf.Mesh(np.asarray(b.vertices,np.float32),np.asarray(b.faces,np.uint32)))
  return (A^Bm).volume()
for name,src,t in [('full-v1.23','/workspace/truedge-mini/ref_truedge_v1.22_body.stl',[0,8.75,0]),('mini-v1.7','/workspace/truedge-mini/work17/model_frame.stl',[0,8.75,-7.555])]:
  body=trimesh.load(src)
  iv=inter(m,body);print(name,'blade∩body volume mm3 %.4f of %.1f'%(iv,m.volume))
  # floating check: distance from blade bottom/top surface samples to body
  s=trimesh.sample.sample_surface(m,3000,seed=2)[0];d=np.abs(trimesh.proximity.signed_distance(body,s))
  print(name,'blade samples within 0.05mm of body: %.0f%%'%(100*(d<0.05).mean()))
  b=m.copy();b.vertices=(m.vertices@R.T+np.array(t))/1000.
  f='/workspace/truedge-colourtext/models/truedge-%s.glb'%name;d=open(f,'rb').read()
  jl=struct.unpack('<I',d[12:16])[0];j=json.loads(d[20:20+jl]);bo=20+jl;bl=struct.unpack('<I',d[bo:bo+4])[0];bin_=bytearray(d[bo+8:bo+8+bl])
  if any(x.get('name')=='blade' for x in j['nodes']):raise SystemExit('already has blade')
  for mm in j['meshes']:mm.pop('extras',None)
  j['asset'].pop('extras',None)
  def add(arr,comp,typ,target):
    while len(bin_)%4:bin_.append(0)
    off=len(bin_);by=arr.tobytes();bin_.extend(by)
    j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(by),'target':target})
    a={'bufferView':len(j['bufferViews'])-1,'componentType':comp,'count':len(arr) if arr.ndim==1 else arr.shape[0],'type':typ}
    if typ=='VEC3':a['min']=arr.min(0).tolist();a['max']=arr.max(0).tolist()
    j['accessors'].append(a);return len(j['accessors'])-1
  # unshared verts per face -> crisp flat normals
  V=b.vertices[b.faces].reshape(-1,3).astype(np.float32);N=np.repeat(b.face_normals,3,0).astype(np.float32);I=np.arange(len(V),dtype=np.uint16)
  ia=add(I,5123,'SCALAR',34963);pa=add(V,5126,'VEC3',34962);na=add(N,5126,'VEC3',34962)
  j['materials'].append({'name':'blade_steel','pbrMetallicRoughness':{'baseColorFactor':[0.578,0.603,0.630,1],'metallicFactor':1.0,'roughnessFactor':0.35}})
  j['meshes'].append({'name':'blade','primitives':[{'attributes':{'POSITION':pa,'NORMAL':na},'indices':ia,'mode':4,'material':len(j['materials'])-1}]})
  j['nodes'].append({'name':'blade','mesh':len(j['meshes'])-1});j['scenes'][0]['nodes'].append(len(j['nodes'])-1)
  while len(bin_)%4:bin_.append(0)
  j['buffers']=[{'byteLength':len(bin_)}]
  js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
  out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(bin_))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(bin_),0x004E4942)+bytes(bin_)
  open(f,'wb').write(out);print(name,'glb',len(d),'->',len(out))
