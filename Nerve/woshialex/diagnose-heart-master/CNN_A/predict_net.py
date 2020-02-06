#!/usr/bin/python2
import dsb_utils as du
import config as c
import models as m
import os
import time
import sys

import numpy as np

"""
predict the contour fo the Left Ventricle for all cases 
based on the trained CNN.
"""

M = int(sys.argv[1]);#cases start number (include)
N = int(sys.argv[2]);#cases end number (include)

version = c.net_version;
ss = c.para_ss;
noc = c.no_contour_type;
tag = c.tag;
vvv = "p2090_size{}_ss{}_noc{}_tag{}".format(c.fcn_img_size,ss,noc,tag);
res_file = 'v{}_'.format(version)+vvv + '_2norm';
train_CV = False
pct_norm = (10,90);
pct_norm2 = (20,99);
generate_contours = 0;
if noc == 'auto':
    generate_contours = 0;

np.random.seed(2345)
#compare with 1 (10,95)
if train_CV:
    segment_fn = m.get_segmenter_function(c.params_dir, c.fcn_img_size, NCV=5, version=version, param_file_key=vvv);
else:
    segment_fn = m.get_segmenter_function(c.params_dir + '/fcn_v{}_{}_f5.npz'.format(version,vvv), c.fcn_img_size, NCV=False, version=version);

label_map = du.get_label_map(os.path.join(c.data_kaggle, 'train.csv'))
dsets = []

for s in range(M,N+1):
    start = time.time()
    dset = du.CNN_Dataset(s)
    if len(dset.slices_ver) < 3:
        pass
    dset.segment(segment_fn, 
            segment_transform = lambda x:du.segmenter_data_transform(x, rotate=None, normalize_pctwise=pct_norm),\
            segment_transform2 = lambda x:du.segmenter_data_transform(x, rotate=None, normalize_pctwise=pct_norm2));

    #plt.imshow(dset.counts)
    #plt.show()
    sys_vol, dias_vol = dset.calculate_areas();
    print '{} - #{} s={} t={} {:0.2f} sec, {} {}'.format(len(dsets), dset.name, len(dset.slices_ver), len(dset.time), time.time()-start, dset.sys_vol, dset.dias_vol)
    if s in label_map:
        edv, esv = label_map[s]
        print esv, edv, dset.sys_vol-esv,dset.dias_vol-edv
        #if s<=generate_contours:##save contours
        #    i_s,i_d = dset.areas_cutoff(esv,edv);
        #    if i_s>0:
        #        for k in range(i_s):
        #            du.save_imgcon((s,k,dset.sys_time),dset.images[k,dset.sys_time,0],None);
        #        du.save_imgcon((s,i_s,dset.sys_time),dset.images[i_s,dset.sys_time,0],dset.seg_binary[i_s*len(dset.time)+dset.sys_time,0]);
        #    if i_d>0:
        #        for k in range(i_d):
        #            du.save_imgcon((s,k,dset.dias_time),dset.images[k,dset.dias_time,0],None);
        #        du.save_imgcon((s,i_d,dset.dias_time),dset.images[i_d,dset.dias_time,0],dset.seg_binary[i_d*len(dset.time)+dset.dias_time,0]);

    dsets.append(dset)
    dset.unload()
if M==1:#from the beginning
    style = 'w';#remove previous files
else:
    style = 'a';#append
du.write_outputs(dsets, c.output_dir, vvv=res_file, style=style)
