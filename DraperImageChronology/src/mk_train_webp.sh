
TRAIN_DIR=../download/train
OUT_DIR=../data/train.webp

# note: -lossless option underperforms
# QUALITY=100    # 0=worst 100=best 

QUALITY=0    # 0=worst 100=best 


for f in `ls ${TRAIN_DIR}/* | sort -V`
do
    echo
    # cwebp -lossless -q ${QUALITY} $f -o ${OUT_DIR}/`basename $f .tif`.webp # underperforms 
    cwebp -q ${QUALITY} $f -o ${OUT_DIR}/`basename $f .tif`.webp
    echo
done

