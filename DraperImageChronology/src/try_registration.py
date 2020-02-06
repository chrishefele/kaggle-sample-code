import os
import scipy as sp
import scipy.misc
import imreg_dft as ird
import itertools # permutations('abcd', 2)

basedir = '../data/resized.images'

# the baseline image
im0 = sp.misc.imread(os.path.join(basedir, "set10_1.jpeg"), flatten=True) 

# the image to be transformed to match the baseline image
im1 = sp.misc.imread(os.path.join(basedir, "set12_1.jpeg"), flatten=True) # the image to be transformed

results = ird.imreg.similarity(im0, im1)

tvec_y, tvec_x  = results['tvec']
scale           = results['scale']
angle           = results['angle']
success         = results['success']

for key in ['scale', 'angle', 'tvec', 'success']:

    if key == 'tvec':
        tvec_y, tvec_x = results['tvec']
        print 'tvec_x', "=", tvec_x
        print 'tvec_y', "=", tvec_y
    else:
        print key, "=", results[key]

