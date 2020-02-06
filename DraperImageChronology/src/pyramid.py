
import cv2
import sys
import os, os.path

CHANNELS   = 3 # RGB
MIN_PIXELS = 1 * 1 * CHANNELS

inpath = sys.argv[1]
outdir = sys.argv[2]

img = cv2.imread(inpath)

base      = os.path.basename(inpath)
fout_tag  = os.path.splitext(base)[0]

downs = 0 
while img.size/CHANNELS > MIN_PIXELS:

    subdir_name = '%02i' % downs
    subdir_path = outdir + '/' + subdir_name
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)

    fout_name = fout_tag + ('-pyrDown-%02i.jpeg' % downs)
    fout_path = outdir + '/' + subdir_name + '/' + fout_name
    cv2.imwrite(fout_path, img)
    print "wrote:", fout_path

    img = cv2.pyrDown(img)
    downs = downs + 1 

print
