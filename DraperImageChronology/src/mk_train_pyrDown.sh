
TRAIN_DIR=../download/train
OUT_DIR=../data/train.pyrDown

for f in `ls ${TRAIN_DIR}/* | sort -V`
do
    python pyramid.py   $f   ${OUT_DIR}
done

