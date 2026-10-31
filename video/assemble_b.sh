cd /workspace/truedge-shop/video
for i in 1 2 3; do
ffmpeg -loglevel error -y -framerate 30 -i n$i/f_%04d.png -vf "scale=1080:1920:flags=lanczos,hqdn3d=0:0:4:4,unsharp=5:5:0.4,fps=30,format=yuv420p" -c:v libx264 -crf 16 -preset slow -r 30 b$i.mp4
done
ffmpeg -loglevel error -y -i b1.mp4 -i b2.mp4 -i b3.mp4 -filter_complex \
"[0:v]settb=1/30,setpts=PTS-STARTPTS[a];[1:v]settb=1/30,setpts=PTS-STARTPTS[b];[2:v]settb=1/30,setpts=PTS-STARTPTS[c];[a][b]xfade=transition=fade:duration=0.2667:offset=3.5[ab];[ab][c]xfade=transition=fade:duration=0.2667:offset=7.5,fps=30,format=yuv420p[v]" \
-map "[v]" -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -r 30 -movflags +faststart -an truedge_hero_reveal_v1.22b_9x16.mp4
