
TRAIN_DIR=../download/train
OUT_DIR=../data/train.webp.sizes

# note: -lossless option underperforms
# QUALITY=100    # 0=worst 100=best 

#QUALITY=0    # 0=worst 100=best 
QUALITY=100   # 0=worst 100=best 

for f in `ls ${TRAIN_DIR}/* | sort -V`
do
    echo
    echo processing $f
    echo
    for width in 3100 1550 775 388 194 96
    do

        echo file: $f width: $width 
        cwebp -q ${QUALITY} -resize ${width} 0  $f -o ${OUT_DIR}/${width}/`basename $f .tif`.webp & 
        echo

    done
    wait 
done

