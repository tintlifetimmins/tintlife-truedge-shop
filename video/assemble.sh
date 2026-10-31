# $1 prefix (s|h) $2 out
cd /workspace/truedge-shop/video
ffmpeg -loglevel error -y -framerate 30 -i ${1}1/f_%04d.png -framerate 30 -i ${1}2/f_%04d.png -framerate 30 -i ${1}3/f_%04d.png -filter_complex \
"[0:v]fps=30,format=yuv420p,settb=1/30,setpts=PTS-STARTPTS[a];[1:v]fps=30,format=yuv420p,settb=1/30,setpts=PTS-STARTPTS[b];[2:v]fps=30,format=yuv420p,settb=1/30,setpts=PTS-STARTPTS[c];\
[a][b]xfade=transition=fade:duration=0.2667:offset=3.5[ab];[ab][c]xfade=transition=fade:duration=0.2667:offset=7.5[v]" \
-map "[v]" -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -r 30 -movflags +faststart -an $2
