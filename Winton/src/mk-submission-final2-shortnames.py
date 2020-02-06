
from shutil import copyfile
import os, os.path, sys
import shutil

SOURCE_DIR = "../submissions/final2"
DEST_DIR   = "../submissions/final2.shortnames"

def shortenable(fname):
    tokens = fname.split("_")
    predcol = int(tokens[7].split(".")[0])
    return predcol == 62

def shorten(fname):
    # sub_0001_f7_75916_scale_-0.20_pred_61.csv  --->  sub_0001_0.20.csv 
    tokens = fname.split("_")
    fname_new = "_".join( [tokens[0], tokens[1], str(abs(float(tokens[5]))) ] ) + ".csv"
    return fname_new

for fn in sorted(next(os.walk(SOURCE_DIR))[2]):

    if not shortenable(fn):
        continue

    src_file = os.path.join(SOURCE_DIR, fn)
    dst_file = os.path.join(DEST_DIR, shorten(fn))
    print "copying:", src_file, "->", dst_file
    copyfile(src_file, dst_file)

