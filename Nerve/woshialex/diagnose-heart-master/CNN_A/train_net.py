#!/usr/bin/python2
import theano
import theano.tensor as T
import lasagne as nn
from lasagne.layers import batch_norm as bn

import os

import utils as u
from models import *

if __name__=='__main__':
    """
    build and train the CNNs.
    """
    import numpy as np
    import dsb_utils as du
    import config as c
    import sys

    CV = c.do_cv;
    pct_norm_tr = ((1,20),(90,100));
    pct_norm = (10,95);
    num_epochs = c.num_epochs;
    version = c.net_version;
    noc = c.no_contour_type;
    ss = c.para_ss;
    tag = c.tag;
    datafile = 'scd_seg_noc{}_{}.hdf5'.format(noc,c.fcn_img_size)
    vvv = "p2090_size{}_ss{}_noc{}_tag{}".format(c.fcn_img_size,ss,noc,tag);
    shi = c.shift;
    rot = c.rotation;
    sca = c.scale;

    ntimes  = 6; #NCV+1
    np.random.seed(1234);
    input_var = T.tensor4('input')
    label_var = T.tensor4('label')
    net, output, output_det =build_fcn_segmenter(input_var, (None, 1, c.fcn_img_size, c.fcn_img_size), version)
    for l in nn.layers.get_all_layers(net['output']):
        print nn.layers.get_output_shape(l)
    params = nn.layers.get_all_params(net['output'], trainable=True)
    init0 = nn.layers.get_all_param_values(net['output']);

    lr = theano.shared(nn.utils.floatX(3e-3))
    loss = du.sorenson_dice(output, label_var,ss=ss)
    te_loss = du.sorenson_dice(output_det, label_var,ss=ss)
    te_acc = nn.objectives.binary_accuracy(output_det, label_var).mean()
    updates = nn.updates.adam(loss, params, learning_rate=lr)
    train_fn = theano.function([input_var, label_var], loss, updates=updates)
    test_fn = theano.function([input_var, label_var], te_loss)
    acc_fn = theano.function([input_var, label_var], te_acc)
    pred_fn = theano.function([input_var], output_det)


    batch_size=16
    max_epoch = (0 if CV else num_epochs);
    for i in xrange(ntimes):
        if not CV and i!=5:
            continue
        if i == 5:
            num_epochs = max_epoch+1;
            print("full train data use {:d} epochs".format(num_epochs))
        nn.layers.set_all_param_values(net['output'],init0);
        data = u.DataH5PyStreamer(os.path.join(c.data_sunnybrook, datafile), batch_size=batch_size, folds=(5,i))
        hist,best_epoch = u.train_with_hdf5(data, num_epochs=num_epochs, train_fn = train_fn, test_fn=test_fn,
                            max_per_epoch=-1,
                            tr_transform=lambda x: du.segmenter_data_transform(x, shift=shi, rotate=rot, scale = sca, normalize_pctwise=pct_norm_tr),
                            te_transform=lambda x: du.segmenter_data_transform(x, normalize_pctwise=pct_norm,istest=True),
                            last_layer = net['output'],
                            save_best_params_to=c.params_dir + '/fcn_v{}_{}_f{}.npz'.format(version, vvv,i))
        if i < 5 and best_epoch>max_epoch:
            max_epoch = best_epoch;
    if CV:
        for pfn in ['fcn_v{}_{}_f{}.npz'.format(version, vvv, i) for i in xrange(ntimes-1)]:#!!!!CHANGE
            u.load_params(net['output'], os.path.join(c.params_dir, pfn))
            testfold = int(pfn.split('_')[-1][1])
            data = u.DataH5PyStreamer(os.path.join(c.data_sunnybrook, datafile),
                                      batch_size=16, folds=(5,testfold))
            streamer = data.streamer(training=False, shuffled=True)

            accs = []
            for imb in streamer.get_epoch_iterator():
                x,y = du.segmenter_data_transform(imb,normalize_pctwise=pct_norm)
                accs.append(acc_fn(x,y))
            print pfn, np.mean(accs)
