import os, sys, numpy as np
import utils as u, config as c, models as m, dsb_utils as du
import theano, theano.tensor as T, lasagne as nn

np.random.seed(1234)
print 'random state seeded segfcn'

def train_model():
    batch_size=8
    version = 2
    total_epochs = c.fcn_train_epochs
    for normpct in [(10,90), None]:
        stop_times = []
        for i in [0,1,2,3,4,-1]:
            num_epochs = int(np.mean(stop_times)) if i == -1 else total_epochs
            data = u.DataH5PyStreamer(os.path.join(c.data_intermediate, 'scd_seg_256.hdf5'),
                                      batch_size=batch_size,folds=(5,i))
            input_var = T.tensor4('input')
            label_var = T.tensor4('label')
            net, output, output_det = m.build_fcn_segmenter(input_var,
                    (None, 1, c.fcn_img_size, c.fcn_img_size), version)
            params = nn.layers.get_all_params(net['output'], trainable=True)

            lr = theano.shared(nn.utils.floatX(3e-3))
            loss = du.sorenson_dice(output, label_var)
            te_loss = du.sorenson_dice(output_det, label_var)
            te_acc = nn.objectives.binary_accuracy(output_det, label_var).mean()
            updates = nn.updates.adam(loss, params, learning_rate=lr)
            train_fn = theano.function([input_var, label_var], loss, updates=updates)
            test_fn = theano.function([input_var, label_var], te_loss)
            pred_fn = theano.function([input_var], output_det)

            normstr = (str(normpct[0]) + str(normpct[1])) if normpct else 'MS'
            pfn = os.path.join(c.params_dir, 'fcn_v{}_p{}/fcn_v{}_p{}_f{}_{}.npz'.format(
                    version, normstr, version, normstr, i, np.random.randint(100000)))
            hist = u.train_with_hdf5(data, num_epochs=num_epochs,
                    train_fn = train_fn, test_fn=test_fn,
                    max_per_epoch=-1,
                    tr_transform=lambda x: du.segmenter_data_transform(x,
                        rotate=(-10, 50), normalize_pctwise=normpct),
                    te_transform=lambda x: du.segmenter_data_transform(x,
                        rotate=None, normalize_pctwise=normpct),
                    use_tqdm = False,
                    last_layer = net['output'],
                    save_last_params = (i == -1),
                    save_params_to=pfn)
            if i != -1:
                stop_times.append(np.argmin(np.array(hist)[:,1])+1)
                print 'stop time {}'.format(stop_times[-1])

def evaluate():
    label_map = du.get_label_map(os.path.join(c.data_kaggle, 'train.csv'))
    normdict = {'p1090': (10,90), 'pMS':None}
    for pstr in ['pMS', 'p1090']:
        segment_fn = m.get_segmenter_function(os.path.join(c.params_dir, 'fcn_v2_' + pstr),
                c.fcn_img_size, ensemble=True, version=2)
        dsets = []
        for s in range(*c.fcn_eval_cases):
            dset = du.CNN_Dataset(s)
            if len(dset.slices_ver) < 5:
                pass
            dset.segment(segment_fn, lambda x:du.segmenter_data_transform(x, rotate=None,
                normalize_pctwise=normdict[pstr]))
            sys_vol, dias_vol = du.calculate_areas(dset, dset.counts, dset.sys_time,
                dset.dias_time, end_slice_include=False)
            sys_vol = max(sys_vol, 0.15*dias_vol)
            dset.sys_vol, dset.dias_vol= (sys_vol, dias_vol)
            print '#{} {} {}'.format(dset.name, sys_vol, dias_vol)
            dsets.append(dset)
            dset.unload()
        #vector_map = { int(ds.name):([1, ds.sys_vol], [1, ds.dias_vol]) for ds in dsets }
        #w_func = du.optimize_w(vector_map, label_map, 2, max_w = 8, above_below=True)
        du.write_outputs(dsets, c.output_dir, pstr)
