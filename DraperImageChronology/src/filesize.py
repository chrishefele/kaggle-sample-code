
import os, os.path
import sys
import glob
import scipy.stats
import string
import numpy 

TIF_DIR_TRAIN = "../download/train"
TIF_DIR_TEST  = "../download/test"

def get_set_order(fprefix):
    # example: from "set123_4" return (123, 4) s = ''.join(c if c in string.digits else ' ' for c in fprefix)
    s = ''.join(c if c in string.digits else ' ' for c in fprefix)
    n_set, n_order = s.split()[0:2]
    n_set = int(n_set)
    n_order = int(n_order)
    return (n_set, n_order)

def get_tif_size(fset, forder):
    tif_name = "set" + str(fset) + "_" + str(forder) + ".tif"
    tif_path_train = TIF_DIR_TRAIN + "/" + tif_name
    tif_path_test  = TIF_DIR_TEST  + "/" + tif_name
    if os.path.isfile(tif_path_train):
        tif_path = tif_path_train
    elif os.path.isfile(tif_path_test):
        tif_path = tif_path_test
    else:
        raise RuntimeError, tif_name + " not found"
    tif_size = os.path.getsize(tif_path)
    return tif_size

def get_path_rankcor(path):

    image_paths = list(sorted(glob.glob(path)))

    forders = []
    fsizes  = []
    rcors   = []

    for image_path in image_paths:

        fname   = os.path.basename(image_path)
        fprefix = os.path.splitext(fname)[0]
        fset, forder  = get_set_order(fprefix)
        fsize   = os.path.getsize(image_path)  
        tif_size = get_tif_size(fset, forder)

        forders.append(forder)

        # generally, compression ratio worked better than file size alone
        # compression_ratio = float(fsize) / float(tif_size)
        # fsizes.append(compression_ratio)
        fsizes.append(fsize) 

        if forder == 5:

            rcor, pval = scipy.stats.spearmanr(forders, fsizes)
            rcors.append(rcor)
            #print "set:", fset, forders, fsizes, rcor

            forders = []
            fsizes  = []
            
    rcors_a = numpy.array(rcors)
    results = (path, rcors_a.mean(), numpy.median(rcors_a))
    print "RESULT: %40s mean: %10.5f median: %10.5f" % results
    rcors_a = numpy.around(rcors_a, decimals=3)
    print numpy.sort(rcors_a)
    print rcors_a

# ---------------- MAIN -------------

get_path_rankcor("../download/test_sm/*.jpeg")
get_path_rankcor("../download/test/*.tif")

get_path_rankcor("../download/train_sm/*.jpeg")
get_path_rankcor("../download/train/*.tif")
get_path_rankcor("../data/train.webp/*.webp")
get_path_rankcor("../data/train.jpeg/*.jpeg")
get_path_rankcor("../data/train.RGB/*RGB_0.jpeg")
get_path_rankcor("../data/train.RGB/*RGB_1.jpeg")
get_path_rankcor("../data/train.RGB/*RGB_2.jpeg")

widths = [3100, 1550, 775, 388, 194, 96]
for width in widths:
    get_path_rankcor("../data/train.webp.sizes/%i/*.webp" % width)

for downs in range(12):
    get_path_rankcor("../data/train.pyrDown/%02i/*" % downs)

#get_path_rankcor("../download/test/*.tif")
#get_path_rankcor("../download/train/*.tif")

