# histograms of downloaded images

srcdir_train=../download/train
dstdir_train=../data/train.hist

srcdir_test=../download/test
dstdir_test=../data/test.hist

for fimage in ${srcdir_train}/*
do
    echo ${fimage}
    convert ${fimage} histogram:${dstdir_train}/`basename ${fimage} .tif`.png
done

for fimage in ${srcdir_test}/*
do
    echo ${fimage}
    convert ${fimage} histogram:${dstdir_test}/`basename ${fimage} .tif`.png
done

