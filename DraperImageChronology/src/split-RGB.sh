


# from http://www.imagemagick.org/Usage/color_basics/


#convert rose: -channel R -separate separate_red.gif
#convert rose: -channel G -separate separate_green.gif
#convert rose: -channel B -separate separate_blue.gif

srcdir_train=../download/train_sm
srcdir_test=../download/test_sm
dstdir=../data/train.RGB

for fimage in ${srcdir_train}/*
do

    echo $fimage
    # fills in %d -- 0=Red, 1=Green, 2=Blue
    convert ${fimage} -separate ${dstdir}/`basename ${fimage} .jpeg `_RGB_%d.jpeg
    echo

done


