#
# Create clip files derived from Whale Redux train + test sets
# to be used with code from the original Whale contest
# (filename format, sizes, etc. differed between the contests)
# Use "rightsize" script to force all clips to the same length
# Also create a train.csv file, similar to what was used in the orignal contest
#

SRC=../download
DST=../data_WhaleRedux2

# create new train.csv with sequential clip names & training labels
ls $SRC/train2 | awk ' 
    BEGIN    { fctr=0;  print "clip_name,label"    } 
    /_0.aif/ { fctr+=1; print "train"fctr".aiff,0" } 
    /_1.aif/ { fctr+=1; print "train"fctr".aiff,1" } 
' > $DST/train.csv 


# rightsize audio clips from TRAIN set & give new numbered filenames
fctr=0
ls $SRC/train2 | while read fsrc
do
   fctr=$(( fctr + 1 ))
   fdst=train${fctr}.aiff
   ./rightsize_clip.sh  $SRC/train2/$fsrc  $DST/train/$fdst
done


# rightsize audio clips from TEST set & give new numbered filenames
fctr=0
ls $SRC/test2 | while read fsrc
do
   fctr=$(( fctr + 1 ))
   fdst=test${fctr}.aiff
   ./rightsize_clip.sh  $SRC/test2/$fsrc  $DST/test/$fdst
done

