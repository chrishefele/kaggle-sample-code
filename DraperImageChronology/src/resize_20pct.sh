# Put reduced-size versions of all images in a single directory 

RESIZE="20%"   # for ird, about 1.2 sec/image for 10%, or 4 sec/image for 20%

srcdir_train=../download/train_sm
srcdir_test=../download/test_sm
dstdir=../data/resized.20pct

for fimage in ${srcdir_train}/*_1.jpeg
do
    convert -verbose -resize ${RESIZE} ${fimage} ${dstdir}/`basename ${fimage}`
    echo
done

for fimage in ${srcdir_test}/*_1.jpeg
do
    convert -verbose -resize ${RESIZE} ${fimage} ${dstdir}/`basename ${fimage}`
    echo
done

