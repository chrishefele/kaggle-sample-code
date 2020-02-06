# Copy datafiles from original Whale challenge 
# Use "rightsize" script on them for consistency with file processing 
# used in the WhaleRedux challeng

SRC=../data
DST=../data_Whale

cp $SRC/train.csv $DST/train.csv

for f in $SRC/train/*
do
   fname=`basename $f`
   ./rightsize_clip.sh  $SRC/train/$fname  $DST/train/$fname
done

for f in $SRC/test/*
do
   fname=`basename $f`
   ./rightsize_clip.sh  $SRC/test/$fname  $DST/test/$fname
done

