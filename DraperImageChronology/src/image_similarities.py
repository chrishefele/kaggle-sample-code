
import os, os.path
import scipy as sp
import scipy.misc
import imreg_dft as ird
import sys

files = sys.argv[1:]

print "file_base, file_transformed, success, scale, angle, tvec_x, tvec_y"

for f1 in files:

    # the baseline image
    im0 = sp.misc.imread(f1, flatten=True) 

    for f2 in files:

        if f1 == f2: 
            continue

        # the image to be transformed to match the baseline image
        im1 = sp.misc.imread(f2, flatten=True) 
        
        try:
            results = ird.imreg.similarity(im0, im1)
        except ValueError:
            continue

        tvec_y, tvec_x  = results['tvec']
        scale           = results['scale']
        angle           = results['angle']
        success         = results['success']

        items = [os.path.basename(f1), os.path.basename(f2), 
                 success, scale, angle, tvec_x, tvec_y]
        print ' , '.join([str(item) for item in items])


