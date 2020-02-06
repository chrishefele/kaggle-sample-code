
import os, os.path
import scipy as sp
import scipy.misc
import imreg_dft as ird
import sys

SET_MAX = 344

DIR_SRC = "../data/resized.images/"
DIR_DST = "../data/training.image.diffs/"


sets_train = [ \
    4, 5, 10, 12, 16, 20, 21, 25, 29, 31, 35, 43, 44, 
    50, 53, 57, 58, 59, 69, 78, 79, 94, 97, 107, 112, 131, 
    137, 143, 144, 158, 160, 165, 171, 173, 175, 176, 178,
    190, 194, 201, 203, 205, 211, 217, 218, 220, 223, 224,
    229, 239, 241, 251, 252, 255, 257, 264, 268, 274, 277,
    279, 285, 297, 298, 301, 303, 307, 311, 327, 340, 342 ]

#for set_num in range(1, SET_MAX + 1):
# for set_num in [8, 18, 36, 38, 44, 143, 22, 189, 79, 101, 67, 53, 63, 84]: 
for set_num in sets_train:

    for suffix_base  in range(1,5+1):
        for suffix_trans in range(1,5+1):

            f0_prefix = "set" + str(set_num) + "_" + str(suffix_base)  
            f1_prefix = "set" + str(set_num) + "_" + str(suffix_trans) 
            
            f0 = f0_prefix + ".jpeg"
            f1 = f1_prefix + ".jpeg"

            # the baseline image
            im0 = sp.misc.imread(DIR_SRC + f0, flatten=True) 

            # the image to be transformed to match the baseline image
            im1 = sp.misc.imread(DIR_SRC + f1, flatten=True) 
                
            try:
                results = ird.imreg.similarity(im0, im1)
            except ValueError:
                continue

            new_image = results['timg']

            fout = DIR_DST + f0_prefix + "__" + f1_prefix + "__transform.jpeg"
            sp.misc.imsave(fout, new_image)
            print "wrote:", fout

            fout = DIR_DST + f0_prefix + "__" + f1_prefix + "__baseline.jpeg"
            sp.misc.imsave(fout, im0)
            print "wrote:", fout
            print

