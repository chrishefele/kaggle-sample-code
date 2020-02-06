# Put reduced-size versions of all images in a single directory 

RESIZE="10%"   # for ird, about 1.2 sec/image for 10%, or 4 sec/image for 20%

srcdir_train=../download/train_sm
srcdir_test=../download/test_sm
dstdir=../data/resized.images

for fimage in ${srcdir_train}/*
do
    convert -verbose -resize ${RESIZE} ${fimage} ${dstdir}/`basename ${fimage}`
    echo
done

for fimage in ${srcdir_test}/*
do
    convert -verbose -resize ${RESIZE} ${fimage} ${dstdir}/`basename ${fimage}`
    echo
done

