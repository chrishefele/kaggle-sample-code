
TRAIN_DIR=../download/train
OUT_DIR=../data/train.jpeg

# QUALITY=10   # 1=worst 100=best 

for f in `ls ${TRAIN_DIR}/* | sort -V`
do
    # echo $f
    #convert -quality ${QUALITY} $f ${OUT_DIR}/`basename $f .tif`.jpeg
    convert -verbose -resize 50%     $f    ${OUT_DIR}/`basename $f .tif`.jpeg
    echo 
done

