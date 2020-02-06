# Put reduced-size versions of all images in a single directory 

RESIZE="30%"   # for ird, about 1.2 sec/image for 10%, or 4 sec/image for 20%

srcdir_train=../download/train_sm
srcdir_test=../download/test_sm
dstdir=../data/resized.30pct

for fimage in ${srcdir_train}/*.jpeg
do
    convert -verbose -resize ${RESIZE} ${fimage} ${dstdir}/`basename ${fimage}`
    echo
done

for fimage in ${srcdir_test}/*.jpeg
do
    convert -verbose -resize ${RESIZE} ${fimage} ${dstdir}/`basename ${fimage}`
    echo
done

