cd /workspace/truedge-shop/video
R=$1; P=$2
SW=6 SPP=16 FS=1 FE=113 ./go.sh 1 $R $PWD/${P}1
SW=8 SPP=16 FS=1 FE=128 ./go.sh 2 $R $PWD/${P}2
SW=2 SPP=16 FS=1 FE=120 ./go.sh 3 $R $PWD/${P}3
echo ALLDONE $P
