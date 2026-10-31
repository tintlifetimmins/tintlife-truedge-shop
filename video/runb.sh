cd /workspace/truedge-shop/video
EXPO=-1.3 SW=10 SPP=24 FS=1 FE=113 ./go.sh 1 720x1280 $PWD/n1
EXPO=-1.6 SW=10 SPP=24 FS=1 FE=128 ./go.sh 2 720x1280 $PWD/n2
EXPO=-1.6 SW=3 SPP=24 FS=1 FE=120 ./go.sh 3 720x1280 $PWD/n3
echo ALLDONE
