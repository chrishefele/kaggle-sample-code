# histograms of downloaded images

srcdir_train=../download/train_sm
dstdir_train=../data/train_sm.hist

srcdir_test=../download/test_sm
dstdir_test=../data/test_sm.hist

for fimage in ${srcdir_train}/*
do
    echo ${fimage}
    convert ${fimage} histogram:${dstdir_train}/`basename ${fimage} .jpeg`.png
done

for fimage in ${srcdir_test}/*
do
    echo ${fimage}
    convert ${fimage} histogram:${dstdir_test}/`basename ${fimage} .jpeg`.png
done

