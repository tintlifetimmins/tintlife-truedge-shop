cd /workspace/truedge-shop/renders_v1.22/build
export ALB=0.8 FRONT=${FRONT:-0.625} STL=$PWD/truedge_v1.22_body_nosupport.stl TL_DARK=1 TILE=1
# $1 shot $2 res $3 outdir, extra env passes through
SHOT=$1 RES=$2 OUT=$3 blender -b -t 8 -P /workspace/truedge-shop/video/anim.py -- 000000 pla /tmp/x.png 24 -3.0 100 noblade </dev/null 2>&1 | grep -E "Saved|rror|Time:" 
