import time
import sys
import os
from PIL import Image
import numpy as np

import lasagne as nn
import theano
import theano.tensor as T

import h5py
from fuel.datasets.hdf5 import H5PYDataset
from fuel.schemes import ShuffledScheme, SequentialScheme
from fuel.streams import DataStream

# runs training loop, expects data in DataH5PYStreamer format
# tr_transform and te_transform must return list or tuple, to allow
# for situations where the functions require 2+ inputs
def train_with_hdf5(data, num_epochs, train_fn, test_fn,
        tr_transform = lambda x:x,
        te_transform = lambda x:x,
        verbose=True, train_shuffle=True,
        save_best_params_to=None,
        last_layer=None,
        max_per_epoch=-1):
    tr_stream = data.streamer(training=True, shuffled=train_shuffle)
    te_stream = data.streamer(training=False, shuffled=False)
    from tqdm import tqdm
    ret = []
    mve_params = None
    mve = None
    best_epoch = 0;
    for epoch in range(num_epochs):
        start = time.time()
        tr_err, tr_batches = 0,0
        for imb in tqdm(tr_stream.get_epoch_iterator(), total=data.ntrain/data.batch_size):
            if imb[0].shape[0] != data.batch_size:
                continue
            imb = tr_transform(imb)
            if not isinstance(imb, tuple):
                imb = (imb,)
            tr_err += train_fn(*imb)
            tr_batches += 1
            if max_per_epoch > 0 and tr_batches > max_per_epoch:
                break
        tr_err /= tr_batches

        val_err, val_batches = 0,0
        if te_stream is not None:
            for imb in tqdm(te_stream.get_epoch_iterator(), total=data.ntest/data.batch_size):
                if imb[0].shape[0] != data.batch_size:
                    continue
                imb = te_transform(imb)
                if not isinstance(imb, tuple):
                    imb = (imb,)
                val_err += test_fn(*imb)
                val_batches += 1
                if max_per_epoch > 0 and val_batches > max_per_epoch:
                    break
            val_err /= val_batches
            if save_best_params_to is not None:
                if mve is None or val_err < mve:
                    mve = val_err
                    mve_params = [np.copy(p) for p in (nn.layers.get_all_param_values(last_layer))]
                    best_epoch = epoch;
        if verbose:
            print('ep {}/{} - tl {:.5f} - vl {:.5f} - t {:.3f}s'.format(
                epoch, num_epochs, tr_err, val_err, time.time()-start))
        ret.append((tr_err, val_err))

    if mve_params is None:
        best_epoch = epoch;
        mve_params = [np.copy(p) for p in (nn.layers.get_all_param_values(last_layer))]
    if save_best_params_to is not None:
        print("save best epoch: {:d}".format(best_epoch));
        save_params(mve_params, save_best_params_to)
    return ret,best_epoch

# goes from raw image array (usually uint8) to floatX, square=True crops to
# size of the short edge, center=True crops at center, otherwise crop is
# random
def raw_to_floatX(imb, pixel_shift=0.5, square=True, center=False, rng=None):
    rng = rng if rng else np.random
    w,h = imb.shape[2], imb.shape[3] # image size
    x, y = 0,0 # offsets
    if square:
        if w > h:
            if center:
                x = (w-h)/2
            else:
                x = rng.randint(w-h)
            w=h
        elif h > w:
            if center:
                y = (h-w)/2
            else:
                y = rng.randint(h-w)
            h=w
    return nn.utils.floatX(imb)[:,:,x:x+w,y:y+h]/ 255. - pixel_shift


# for organizing an hdf5 file for streaming
class DataH5PyStreamer:
    # folds = None if dataset is separated into 'train', 'test'
    # folds = (10, 3) for ex if there are 10 total folds and #3 (zero_indexed) is validation set
    # folds = (10, 10) use all folds as train and no test
    def __init__(self, h5filename, ntrain=None, ntest=None, batch_size=1, folds=None):
        if folds is None:
            te_sets = ('test',)
            tr_sets = ('train',)
        else:
            notest = (folds[0] == folds[1]);
            te_sets = () if notest else ('fold_{}'.format(folds[1]),)
            tr_sets = tuple(['fold_{}'.format(i) for i in range(folds[0]) if i != folds[1]])
        self.batch_size = batch_size
        self.tr_data = H5PYDataset(h5filename, which_sets=tr_sets)
        self.te_data = None if notest else H5PYDataset(h5filename, which_sets=te_sets)
        self.ntrain = ntrain or self.tr_data.num_examples
        self.ntest = ntest or self.te_data.num_examples if self.te_data else 0

    def dataset(self, training=True):
        return self.tr_data if training else self.te_data
    def streamer(self, training=True, shuffled=False):
        n = self.ntrain if training else self.ntest
        if n==0:
            return None;
        func = ShuffledScheme if shuffled else SequentialScheme
        sch = func(examples=n, batch_size=self.batch_size)
        data = self.tr_data if training else self.te_data
        return DataStream(data, iteration_scheme = sch)

# helper function for building vae's
def log_likelihood(tgt, mu, ls):
    return T.sum(-(np.float32(0.5 * np.log(2 * np.pi)) + ls)
            - 0.5 * T.sqr(tgt - mu) / T.exp(2 * ls))

# from the array used for testing, to the kind used in Image.fromarray(..)
def get_picture_array(X, index, shift=0.5):
    ch, w, h = X.shape[1], X.shape[2], X.shape[3]
    ret = ((X[index]+shift)*255.).reshape(ch,w,h).transpose(2,1,0).clip(0,255).astype(np.uint8)
    if ch == 1:
        ret=ret.reshape(h,w)
    return ret

# returns an Image with X on top, Xpr on bottom, index as requeseted or random if -1
def get_image_pair(X, Xpr,index=-1,shift=0.5):
    mode = 'RGB' if X.shape[1] == 3 else 'L'
    index = np.random.randint(X.shape[0]) if index == -1 else index
    original_image = Image.fromarray(get_picture_array(X, index,shift=shift),mode=mode)
    new_size = (original_image.size[0], original_image.size[1]*2)
    new_im = Image.new(mode, new_size)
    new_im.paste(original_image, (0,0))
    rec_image = Image.fromarray(get_picture_array(Xpr, index,shift=shift),mode=mode)
    new_im.paste(rec_image, (0,original_image.size[1]))
    return new_im

# gets array (in format used for storage) from an Image
def arr_from_img_storage(im):
    w,h=im.size
    arr=np.asarray(im.getdata(), dtype=np.uint8)
    c = np.product(arr.size) / (w*h)
    return arr.reshape(h,w,c).transpose(2,1,0)

# gets array (in format used for testing) from an Image
def arr_from_img(im,shift=0.5):
    w,h=im.size
    arr=np.asarray(im.getdata(), dtype=theano.config.floatX)
    c = np.product(arr.size) / (w*h)
    return arr.reshape((h,w,c)).transpose(2,1,0) / 255. - shift

# loads params in npz (if filename is a .npz) or pickle if not
def load_params(model, fn):
    if 'npz' in fn:
        with np.load(fn) as f:
            param_values = [f['arr_%d' % i] for i in range(len(f.files))]
        nn.layers.set_all_param_values(model, param_values)
    else:
        with open(fn, 'r') as re:
            import pickle
            nn.layers.set_all_param_values(model, pickle.load(re))

# saves params in npz (if filename is a .npz) or pickle if not
def save_params(model, fn):
    if 'npz' in fn:
        param_vals = model if isinstance(model, list) else nn.layers.get_all_param_values(model)
        np.savez(fn, *param_vals)
    else:
        with open(fn, 'w') as wr:
            import pickle
            pickle.dump(param_vals, wr)

# reset shared variable values of accumulators to recover from NaN
def reset_accs(updates, params):
    for key in updates:
        if not key in params:
            v = key.get_value(borrow=True)
            key.set_value(np.zeros(v.shape,dtype=v.dtype))

# build loss as in (Kingma, Welling 2014) Autoencoding Variational Bayes
def build_vae_loss(input_var, l_z_mu, l_z_ls, l_x_mu_list, l_x_ls_list, l_x_list, l_x,
        deterministic, binary, L):
    layer_outputs = nn.layers.get_output([l_z_mu, l_z_ls] + l_x_mu_list + l_x_ls_list
            + l_x_list + [l_x], deterministic=deterministic)
    z_mu =  layer_outputs[0]
    z_ls =  layer_outputs[1]
    x_mu =  [] if binary else layer_outputs[2:2+L]
    x_ls =  [] if binary else layer_outputs[2+L:2+2*L]
    x_list =  layer_outputs[2:2+L] if binary else layer_outputs[2+2*L:2+3*L]
    x = layer_outputs[-1]
    kl_div = 0.5 * T.sum(1 + 2*z_ls - T.sqr(z_mu) - T.exp(2 * z_ls))
    if binary:
        logpxz = sum(nn.objectives.binary_crossentropy(x, input_var).sum()
                for x in x_list) * (-1./L)
        prediction = x_list[0] if deterministic else x
    else:
        logpxz = sum(log_likelihood(input_var.flatten(2), mu, ls)
            for mu, ls in zip(x_mu, x_ls))/L
        prediction = x_mu[0] if deterministic else T.sum(x_mu, axis=0)/L
    loss = -1 * (logpxz + kl_div)
    return loss, prediction
