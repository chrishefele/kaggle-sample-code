
import os, os.path
import scipy as sp
import scipy.misc
import imreg_dft as ird
import sys
import itertools
import math 
import shutil
import numpy

SET_MAX = 344

#DIR_SRC = "../data/resized.images/"
DIR_SRC = "../data/resized.30pct/"

# TODO 
#DIR_DST = "../data/train.overlap/"
DIR_DST = "../data/test.overlap/" 

setids_all = range(1, SET_MAX+1)

setids_train = [ \
    4, 5, 10, 12, 16, 20, 21, 25, 29, 31, 35, 43, 44, 
    50, 53, 57, 58, 59, 69, 78, 79, 94, 97, 107, 112, 131, 
    137, 143, 144, 158, 160, 165, 171, 173, 175, 176, 178,
    190, 194, 201, 203, 205, 211, 217, 218, 220, 223, 224,
    229, 239, 241, 251, 252, 255, 257, 264, 268, 274, 277,
    279, 285, 297, 298, 301, 303, 307, 311, 327, 340, 342 ]

setids_test = list(sorted( set(setids_all) - set(setids_train) ))

def get_image(setid, fileid):
    f_in = DIR_SRC + "set" + str(setid) + "_" + str(fileid) + ".jpeg"
    return sp.misc.imread(f_in, flatten=True) 

# TODO
#for setid in setids_train:
for setid in setids_test:

    accumulator = []

    for fileid_template in (1,2,3,4,5):

        im_template = get_image(setid, fileid_template)
        sum_log_success = 0.0
        failed = False 
        im_mask = 1
        ims_trans = []

        for fileid_subject in (1,2,3,4,5):

            im_subject  = get_image(setid, fileid_subject)
            try:
                results = ird.imreg.similarity(im_template, im_subject)
            except ValueError:
                failed = True
                continue

            success = results['success']
            scale   = results['scale']
            angle   = results['angle']
            tvec_y, tvec_x  = results['tvec']

            sum_log_success += math.log10(success)

            print "set: %d templ: %i subj: %i succ: %8.3f scale: %6.3f angle: %8.3f tvecX: %8.3f tvecY: %8.3f" % \
                  (setid, fileid_template, fileid_subject, success, scale, angle, tvec_x, tvec_y)

            bgval = ird.utils.get_borderval(im_subject, radius=5)
            im_trans = ird.imreg.transform_img_dict(im_subject, results, bgval=bgval, order=3)
            ims_trans.append((fileid_subject, im_trans))
            im_mask *=  1*(im_trans != bgval)

        if not failed:
            accumulator.append((sum_log_success, fileid_template, im_mask, tuple(ims_trans)))
            print "     set: %d template: %i success: %8.3f" % (setid, fileid_template, sum_log_success)

    accumulator.sort(reverse=True)
    best_success, best_fileid_template, best_im_mask, best_ims_trans = accumulator[0]
    print "BEST set: %d template: %i success: %8.3f" % (setid, best_fileid_template, best_success)
    for fileid_subject, im_trans in best_ims_trans:
        fname = DIR_DST + "set%i_templ%i_subj%i.jpeg" % (setid, best_fileid_template, fileid_subject)
        sp.misc.imsave(fname,  best_im_mask * im_trans)
        #print "wrote:", fname
    print

