import theano
import theano.tensor as T
import lasagne as nn
from lasagne.layers import batch_norm as bn, Conv2DLayer, MaxPool2DLayer
from lasagne.layers import Upscale2DLayer, InputLayer

import os

import utils as u

def build_fcn_segmenter(input_var, shape, version=2):
    ret = {}

    if version == 2:
        ret['input'] = la = InputLayer(shape, input_var)
        ret['conv%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=8, filter_size=7))
        ret['conv%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=16, filter_size=3))
        ret['pool%d'%len(ret)] = la = MaxPool2DLayer(la, pool_size=2)
        ret['conv%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=32, filter_size=3))
        ret['pool%d'%len(ret)] = la = MaxPool2DLayer(la, pool_size=2)
        ret['conv%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=64, filter_size=3))
        ret['pool%d'%len(ret)] = la = MaxPool2DLayer(la, pool_size=2)
        ret['conv%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=64, filter_size=3))
        ret['dec%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=64, filter_size=3,
            pad='full'))
        ret['ups%d'%len(ret)] = la = Upscale2DLayer(la, scale_factor=2)
        ret['dec%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=64, filter_size=3,
            pad='full'))
        ret['ups%d'%len(ret)] = la = Upscale2DLayer(la, scale_factor=2)
        ret['dec%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=32, filter_size=7,
            pad='full'))
        ret['ups%d'%len(ret)] = la = Upscale2DLayer(la, scale_factor=2)
        ret['dec%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=16, filter_size=3,
            pad='full'))
        ret['conv%d'%len(ret)] = la = bn(Conv2DLayer(la, num_filters=8, filter_size=7))
        ret['output'] = la = Conv2DLayer(la, num_filters=1, filter_size=7,
                pad='full', nonlinearity=nn.nonlinearities.sigmoid)

    return ret, nn.layers.get_output(ret['output']), \
            nn.layers.get_output(ret['output'], deterministic=True)

def get_segmenter_function(params_loc, img_size, ensemble=False, version=2,
        param_file_key = '.npz', weight_full_params=0.33):
    shape = (None, 1, img_size, img_size)
    input_var = T.tensor4('input')
    if ensemble:
        expr = 0
        params_files = filter(lambda s: 'v{}'.format(version) in s, os.listdir(params_loc))
        if param_file_key is not None:
            params_files = filter(lambda s: param_file_key in s, params_files)
        full_params_indices = [i for i,a in enumerate(params_files) if 'f-1' in a]
        if len(full_params_indices) > 0:
            wt_norm = (1. - weight_full_params)/(len(params_files) - len(full_params_indices))
            wt_full = weight_full_params / len(full_params_indices)
            params_weights = [(wt_norm if i not in full_params_indices else wt_full) \
                    for i in xrange(len(params_files))]
        else:
            params_weights = [1./len(params_files)] * len(params_files)
        for pfn,w in zip(params_files, params_weights):
            net, _, output_det = build_fcn_segmenter(input_var, shape, version)
            u.load_params(net['output'], os.path.join(params_loc, pfn))
            expr = expr + w*output_det
            print 'loaded {} wt {}'.format(pfn, w)
        print 'loaded {} in ensemble'.format(len(params_files))
    else:
        net, _, output_det = build_fcn_segmenter(input_var, shape, version)
        u.load_params(net['output'], params_loc)
        expr = output_det
        print 'loaded indiv function {}'.format(params_loc)
    return theano.function([input_var], expr)
