import os, sys, cv2, scipy, numpy as np
import dsb_utils as du, config as c, utils as u, models as m
import theano, theano.tensor as T, lasagne as nn

np.random.seed(1234)
print 'random state seeded ch4'

def process_data():
    all_data = []
    img_size = 256
    contour_path= os.path.join(c.data_manual, 'manual_contours_ch4', 'contours')
    image_path = os.path.join(c.data_manual, 'manual_contours_ch4', 'images')
    for fn in [f for f in os.listdir(contour_path) if 'jpg' in f]:
        if not os.path.exists(os.path.join(image_path, fn)):
            continue
        img = cv2.imread(os.path.join(image_path, fn), 0)
        img = cv2.resize(img, (img_size,img_size)).reshape(1,1,img_size,img_size)
        label = cv2.imread(os.path.join(contour_path, fn), 0)
        label = cv2.resize(label, (img_size,img_size))
        _,label = cv2.threshold(label, 127,255,cv2.THRESH_BINARY_INV)
        label = label.reshape(1,1,img_size,img_size)/255
        all_data.append([img,label])
    np.random.shuffle(all_data)
    all_imgs = np.concatenate([a[0] for a in all_data], axis=0)
    all_labels = np.concatenate([a[1] for a in all_data], axis=0)
    n = all_imgs.shape[0]
    destpath = os.path.join(c.data_intermediate, 'ch4_{}.hdf5'.format(img_size))
    if os.path.exists(destpath):
        os.remove(destpath)
    u.save_hd5py({'images': all_imgs, 'labels': all_labels}, destpath, 5)

def train_model():
    batch_size = 16
    num_epochs = c.ch4_train_epochs
    sz = c.fcn_img_size
    version=2
    for i in xrange(5):
        data = u.DataH5PyStreamer(os.path.join(c.data_intermediate, 'ch4_256.hdf5'),
                batch_size=batch_size, folds=(5,i))
        input_var = T.tensor4('input')
        label_var = T.tensor4('label')
        net, output, output_det = m.build_fcn_segmenter(input_var,
                (None, 1, sz, sz), version=version)
        params = nn.layers.get_all_params(net['output'], trainable=True)
        lr = theano.shared(nn.utils.floatX(3e-3))
        loss = du.sorenson_dice(output, label_var)
        te_loss = du.sorenson_dice(output_det, label_var)
        te_acc = nn.objectives.binary_accuracy(output_det, label_var).mean()
        updates = nn.updates.adam(loss, params, learning_rate=lr)
        train_fn = theano.function([input_var, label_var], loss, updates=updates)
        test_fn = theano.function([input_var, label_var], te_loss)
        acc_fn = theano.function([input_var, label_var], te_acc)
        pred_fn = theano.function([input_var], output_det)
        hist = u.train_with_hdf5(data, num_epochs=num_epochs,
                train_fn = train_fn, test_fn=test_fn,
                max_per_epoch=-1, use_tqdm=False,
                tr_transform=lambda x: du.segmenter_data_transform(x, rotate=(-180, 180)),
                te_transform=lambda x: du.segmenter_data_transform(x, rotate=None),
                last_layer = net['output'],
                save_params_to=os.path.join(c.params_dir, 'ch4seg_v{}/test_ch4seg_f{}_v{}.npz'\
                        .format(version, i, version)))

def evaluate():
    ch4_seg_fn = m.get_segmenter_function(os.path.join(c.params_dir, 'ch4seg_v2'),
            c.fcn_img_size, ensemble=True, version=2)
    label_map = du.get_label_map(os.path.join(c.data_kaggle, 'train.csv'))

    # do 4ch segmentation and calculate volume as if it were circular
    calc_map = {}
    print 'segmenting 4ch images and calculating volumes'
    for s in xrange(*c.ch4_eval_cases):
        if s % 10 == 0:
            print 'processing example {}'.format(s)
        dset = du.CNN_Dataset(s, load_sax_images=False)
        if dset.ch4_images is not None:
            dset.segment_ch4(ch4_seg_fn, lambda x: du.segmenter_data_transform(x, rotate=None))
            ch4counts = [np.count_nonzero(ch4s_) for ch4s_ in dset.ch4seg] # count for each time
            if sum(ch4counts) > 0:
                volumes = np.empty(dset.ch4seg.shape[0])
                for t in xrange(dset.ch4seg.shape[0]):
                    diams = np.array([np.count_nonzero(dset.ch4seg[t,:,i])
                        for i in xrange(dset.ch4seg[t].shape[0])])
                    volumes[t] = sum((dset.ch4_line_mult**3)*np.pi*d**2/4 for d in diams)/1000.
                calc_map[s] = min(volumes), max(volumes) 
    out_lines = ['{},{:.2f},{:.2f}\n'.format(s, calc[0], calc[1])
            for s,calc in calc_map.iteritems()]
    with open(os.path.join(c.output_dir, 'ch4_volumes_map.csv'), 'w') as wr:
        wr.writelines(out_lines)

    '''
    # filter data, get rid of any where dias < 40 mL, those tend to be mistakes
    dat = []
    for s in [s_ for s_ in calc_map if s_ in label_map and calc_map[s_][0] > 40]:
        dat.append([label_map[s][0], label_map[s][1], calc_map[s][0], calc_map[s][1]])
    dat = np.array(dat)

    # fit pred_dias=f(raw_dias) to dias, then pred_sys=f(pred_dias, raw_sys) - both linear
    dias_func = np.poly1d(np.polyfit(dat[:,2], dat[:,0], 1))
    def sys_func_wp(pred_dias,pred_sys,lis):
        mult, sl = lis
        return max(mult*pred_dias, sl*pred_sys)
    def sys_func_err(lis):
        return [(sys_func_wp(pd,ps,lis) - rs) for _,rs,pd,ps in dat]
    sys_func2 = np.poly1d(np.polyfit(dat[:,3], dat[:,1], 1))
    obj = scipy.optimize.leastsq(sys_func_err, [.3, .85])
    sys_func = lambda pd,ps: sys_func_wp(pd,ps,obj[0])

    # optimize error as function of predicted values
    calc_vec_map = { s: ([1, sys_func(dias_func(calc[0]), calc[1])],
                        [1, dias_func(calc[0])]) for s,calc in calc_map.iteritems()
                    if calc[0] > 40 }
    print 'optimizing w for 4ch model (this takes a while)'
    wf = du.optimize_w(calc_vec_map, label_map, max_w = 25)

    # eval of errors on train set, and output of combined predictions
    err = 0
    num = 0
    out_lines = []
    print 'evaluation and output for 4ch model'
    for s,(sv, dv) in calc_vec_map.iteritems():
        s_err, d_err = wf(sv,0), wf(dv,1)
        out_lines.append(('{}' + ',{:.4f}'*4 + '\n').format(s, sv[1], s_err, dv[1], d_err))
        if s not in label_map:
            continue
        rd,rs = label_map[s]
        err += 0.5*du.calculate_err(sv[1], rs, s_err, s_err, function=scipy.stats.norm.cdf)
        err += 0.5*du.calculate_err(dv[1], rd, d_err, d_err, function=scipy.stats.norm.cdf)
        num += 1
    print 'train err {} for 4ch model on {} cases'.format(err/num, num)
    with open('output/ch4_predictions_test.csv'.format(np.random.randint(10000)), 'w') as wr:
        wr.writelines(out_lines)
    '''
