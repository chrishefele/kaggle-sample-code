import theano
import theano.tensor as T
import lasagne as nn
from lasagne.layers import batch_norm as bn

import os

import utils as u

def build_fcn_segmenter(input_var, shape, version=1):
    ret = {}
    if version == 1: #for size 256
        ret['input'] = layer = nn.layers.InputLayer(shape, input_var)
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=8, filter_size=5))
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=16, filter_size=3))
        ret['pool{}'.format(len(ret))] = layer = nn.layers.MaxPool2DLayer(layer, pool_size=2)
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=32, filter_size=4))
        ret['pool{}'.format(len(ret))] = layer = nn.layers.MaxPool2DLayer(layer, pool_size=2)
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=64, filter_size=4))
        ret['pool{}'.format(len(ret))] = layer = nn.layers.MaxPool2DLayer(layer, pool_size=2)
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=64, filter_size=5))
        ret['dec{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=64, filter_size=5, pad='full'))
        ret['ups{}'.format(len(ret))] = layer = nn.layers.Upscale2DLayer(layer, scale_factor=2)
        ret['dec{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=32, filter_size=4, pad='full'))
        ret['ups{}'.format(len(ret))] = layer = nn.layers.Upscale2DLayer(layer, scale_factor=2)
        ret['dec{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=16, filter_size=4, pad='full'))
        ret['ups{}'.format(len(ret))] = layer = nn.layers.Upscale2DLayer(layer, scale_factor=2)
        ret['dec{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=8, filter_size=3, pad='full'))
        ret['output'] = layer = nn.layers.Conv2DLayer(layer, num_filters=1, filter_size=5, pad='full',
                                                     nonlinearity=nn.nonlinearities.sigmoid)
    elif version == 2: #for size 196
        ret['input'] = layer = nn.layers.InputLayer(shape, input_var)
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=8, filter_size=5))
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=16, filter_size=3))
        ret['pool{}'.format(len(ret))] = layer = nn.layers.MaxPool2DLayer(layer, pool_size=2)
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=32, filter_size=4))
        ret['pool{}'.format(len(ret))] = layer = nn.layers.MaxPool2DLayer(layer, pool_size=2)
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=64, filter_size=5))
        ret['pool{}'.format(len(ret))] = layer = nn.layers.MaxPool2DLayer(layer, pool_size=2)
        ret['conv{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=128, filter_size=6))
        ret['dec{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=64, filter_size=6, pad='full'))
        ret['ups{}'.format(len(ret))] = layer = nn.layers.Upscale2DLayer(layer, scale_factor=2)
        ret['dec{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=32, filter_size=5, pad='full'))
        ret['ups{}'.format(len(ret))] = layer = nn.layers.Upscale2DLayer(layer, scale_factor=2)
        ret['dec{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=16, filter_size=4, pad='full'))
        ret['ups{}'.format(len(ret))] = layer = nn.layers.Upscale2DLayer(layer, scale_factor=2)
        ret['dec{}'.format(len(ret))] = layer = bn(nn.layers.Conv2DLayer(layer, num_filters=8, filter_size=3, pad='full'))
        ret['output'] = layer = nn.layers.Conv2DLayer(layer, num_filters=1, filter_size=5, pad='full',
                                                     nonlinearity=nn.nonlinearities.sigmoid)
        
    return ret, nn.layers.get_output(ret['output']), \
            nn.layers.get_output(ret['output'], deterministic=True)

def get_segmenter_function(params_loc, img_size, NCV=1, version=1,
        param_file_key = None):
    shape = (None, 1, img_size, img_size)
    input_var = T.tensor4('input')
    if NCV> 1:
        expr = 0
        params_files = filter(lambda s: 'fcn_v{}'.format(version) in s, os.listdir(params_loc))
        if param_file_key is not None:
            params_files = filter(lambda s: param_file_key in s, params_files)
        for pfn in params_files:
            net, _, output_det = build_fcn_segmenter(input_var, shape, version)
            u.load_params(net['output'], os.path.join(params_loc, pfn))
            cv = int(pfn.split('_')[-1][1]);
            if cv == NCV:
                expr = expr + output_det * NCV;
            else:
                expr = expr + output_det
            print 'loaded {}'.format(pfn)
        assert(len(params_files)==NCV+1);
        expr = expr / NCV /2;
        print 'loaded {} in ensemble'.format(len(params_files))
    else:
        net, _, output_det = build_fcn_segmenter(input_var, shape, version)
        u.load_params(net['output'], params_loc)
        expr = output_det
        print 'loaded indiv function {}'.format(params_loc)
    return theano.function([input_var], expr)
