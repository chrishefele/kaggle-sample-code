import os, sys, re, dicom, scipy, cv2
import numpy as np
from skimage import transform, exposure
from sklearn import decomposition
from PIL import Image
from pandas.io.parsers import read_csv

import theano
import theano.tensor as T
import lasagne as nn

import utils as u, config as c
import heart 

def sigmoid(x):
    return 1/(1+np.exp(-x))

def gaussian_pdf(height, center_x, center_y, width_x, width_y, rotation):
    """Returns a pdf function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    rotation = np.deg2rad(rotation)
    center_x = center_x * np.cos(rotation) - center_y * np.sin(rotation)
    center_y = center_x * np.sin(rotation) + center_y * np.cos(rotation)
    def rotgauss(x,y):
        xp = x * np.cos(rotation) - y * np.sin(rotation)
        yp = x * np.sin(rotation) + y * np.cos(rotation)
        g = height*np.exp(
            -(((center_x-xp)/width_x)**2+
              ((center_y-yp)/width_y)**2)/2.)
        return g
    return rotgauss

# doesn't allow for flattening or mean shifting, otherwise occasionally
# we get gaussians that are in the wrong place or drastically the wrong shape
def gaussian_moments_fake(data, normalize_height = False):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    x,y = np.unravel_index(np.argmax(data), data.shape)
    col = data[:, int(y)]
    width_x = np.sqrt(abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max() if not normalize_height else 1
    width = (width_x + width_y)/2
    return height, x, y, width, width, 0.0

class CNN_Dataset(heart.Dataset):
    def resize_square(self):
        ims = self.images
        new_ims = np.empty((ims.shape[0], ims.shape[1], 1, self.img_size, self.img_size), \
                dtype=np.uint8)
        for s in xrange(ims.shape[0]):
            for t in xrange(ims.shape[1]):
                short_edge = min(ims[s,t].shape)
                new_ims[s,t,0] = crop_resize(ims[s,t], self.img_size)
                if t == 0:
                    self.area_multiplier[s] *= (short_edge*1./self.img_size)**2
        self.images = new_ims

    def __init__(self, dset_num, img_size=c.fcn_img_size, direc=None,
            load_sax_images=True, load_ch4_images=True):
        s = str(dset_num)
        if not direc:
            direcs = [os.path.join(c.data_kaggle, 'train'),
                    os.path.join(c.data_kaggle, 'validate'),
                    os.path.join(c.data_kaggle, 'test')]
            direc = next(p for p in direcs if os.path.exists(os.path.join(p, s)))
        super(CNN_Dataset, self).__init__(os.path.join(direc, s), s)
        self.img_size = img_size
        if load_sax_images:
            self.load()
            self.img_size = img_size
            self.resize_square()
        if load_ch4_images:
            self.load_ch4()

    def set_sys_dias_times(self):
        times_totals = self.counts.mean(axis=0)
        self.sys_time, self.dias_time = np.argmin(times_totals), np.argmax(times_totals)

    def segment(self, segment_fn, segment_transform, means=None,stds=None):
        imgs = np.copy(self.images.reshape(-1, 1, self.images.shape[3], self.images.shape[4]))
        imgs = segment_transform(imgs)
        self.segments = np.zeros_like(imgs)
        for i in xrange(imgs.shape[0]):
            self.segments[i:i+1] = segment_fn(imgs[i:i+1])
        self.seg_binary = clean_segmentation(self.segments, self.img_size, 0.5)
        self.counts = np.array([np.count_nonzero(s) for s in self.seg_binary])\
                .reshape(len(self.slices_ver), -1)
        self.set_sys_dias_times()
        self.counts = clean_counts(self.counts, self.sys_time, self.dias_time)
        self.ll = ll_of_count(self.counts, means, stds) \
                if means is not None and stds is not None else 0
        self.areas = np.zeros_like(self.counts, dtype=np.float)
        for si,_ in enumerate(self.slices_ver):
            for ti,_ in enumerate(self.time):
                self.areas[si, ti] = self.counts[si, ti] * self.area_multiplier[si]

    def segment_ch4(self, segment_fn, segment_transform):
        segs = np.zeros_like(self.ch4_images, dtype=np.float32)
        ims = np.copy(self.ch4_images).reshape(-1, 1, self.ch4_images.shape[1],
                self.ch4_images.shape[2])
        ims = segment_transform(ims)
        for i in xrange(self.ch4_images.shape[0]):
            segs[i:i+1] = segment_fn(ims[i:i+1])
            _,sb = cv2.threshold(np.copy(segs[i])*255, 127, 255, cv2.THRESH_BINARY)
            patches = get_patches(sb)
            sb = np.zeros_like(sb, dtype=np.uint8)
            if len(patches) > 0:
                patch = next(p for p in patches if p.shape[0] == max(p1.shape[0]
                    for p1 in patches))
                for x,y in patch:
                    sb[x,y]=255
                pca = decomposition.PCA(n_components=2)
                pca.fit(patch)
                mean, major = pca.mean_, pca.components_[0]
                middle = sb.shape[0]/2
                sb = cv2.warpAffine(sb, np.float32([[1,0,middle-mean[1]],
                    [0,1,middle-mean[0]]]), sb.shape)
                sb = scipy.misc.imrotate(sb, np.arctan2(*major)*180/np.pi)
            segs[i:i+1]=sb
        self.ch4seg = segs
        self.ch4counts = np.array([np.count_nonzero(s) for s in self.ch4seg]).reshape(1,-1)

    def unload(self):
        self.images = None
        self.segments = None
        self.seg_binary = None
        self.ch4seg = None
        self.ch4_images = None

    def load_ch4(self):
        ch4dirs = [d for d in os.listdir(self.directory) if '4ch' in d]
        max_val = 0
        max_dir = None
        self.ch4_images = None
        for d in ch4dirs:
            fn = [f for f in os.listdir(os.path.join(self.directory, d)) if 'dcm' in f][0]
            series = int(f.split('-')[1])
            if series > max_val:
                max_val = series
                max_dir = d
        if max_dir is not None:
            ch4_fns = [f for f in os.listdir(os.path.join(self.directory, max_dir))
                    if 'dcm' in f]
            ch4_fns = sorted(ch4_fns, key=lambda f: int(f.split('.')[0].split('-')[2]))
            ch4_ims = np.empty((len(ch4_fns), self.img_size, self.img_size))
            for i,fn in enumerate(ch4_fns):
                d = dicom.read_file(os.path.join(self.directory, max_dir, fn))
                ch4_ims[i] = crop_resize(d.pixel_array, self.img_size)
                if i == 0:
                    short_edge = min(d.pixel_array.shape)
                    self.ch4_line_mult = float(d.PixelSpacing[0])*short_edge*1./self.img_size
            self.ch4_images = ch4_ims

def calculate_areas(dset, counts, sys_time, dias_time, end_slice_include=True):
    times_totals = counts.mean(axis=0)
    sys_vol, dias_vol = 0,0
    for i in xrange(len(dset.slices_ver)-1):
        thickness = dset.slocation[i+1] - dset.slocation[i]
        # systolic
        a,b = dset.areas[i,sys_time], dset.areas[i+1, sys_time]
        if end_slice_include or (a > 0 and b > 0):
            subvol = (thickness/3.0) * (a + np.sqrt(a*b) + b)
            sys_vol += subvol / 1000.0
        # diastolic
        a,b = dset.areas[i,dias_time], dset.areas[i+1, dias_time]
        if end_slice_include or (a > 0 and b > 0):
            subvol = (thickness/3.0) * (a + np.sqrt(a*b) + b)
            dias_vol += subvol / 1000.0
    return sys_vol, dias_vol

#sorenson-dice
def sorenson_dice(pred, tgt, ss=100):
    #return -2*T.sum(pred*tgt)/(T.sum(pred) + T.sum(tgt) + epsilon)
    return -2*(T.sum(pred*tgt)+ss)/(T.sum(pred) + T.sum(tgt) + ss)

# get_patches deals in 2d arrays of value [0,1]
def get_patches(segment_arr):
    ret = []
    im = segment_arr.astype(np.uint8)*255
    contours = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hulls = [cv2.convexHull(cont) for cont in contours[0]]
    for contour_idx in xrange(len(hulls)):
        cimg = np.zeros_like(im)
        cv2.drawContours(cimg, hulls, contour_idx, color=255, thickness=-1)
        pts = np.array(np.where(cimg == 255)).T
        ret.append(pts)
    return ret

def ll_of_count(counts, means, stds):
    cm = np.copy(counts)
    cm = (cm*255./cm.max()).astype(np.uint8)
    cm = cm[np.where(cm.sum(axis=1))]
    if cm.shape[0] == 0:
        cm = np.zeros((10, 30), dtype = np.uint8)
    im = Image.fromarray(cm).resize((30,10), Image.ANTIALIAS)
    counts_resized_arr = np.array(im.getdata(), dtype=np.float32).reshape(10,30)/255.
    max_ll = -10000000
    for roll_by in xrange(30):
        resized_counts = np.roll(counts_resized_arr, roll_by, axis=1).flatten()
        ll = 0.
        for i in xrange(resized_counts.shape[0]):
            ll += np.log(scipy.stats.norm.pdf(resized_counts[i], loc=means[i], scale=stds[i]))
        if ll > max_ll:
            max_ll = ll
    return max_ll

def clean_segmentation(segments, img_size, thresh):
    mean = segments.mean(axis=(0,1))
    gaussian_params = gaussian_moments_fake(mean, normalize_height=True)
    pdf = gaussian_pdf(*gaussian_params)
    seg_binary = np.zeros_like(segments)
    pdf_dict = np.zeros_like(mean)
    for x in xrange(mean.shape[0]):
        for y in xrange(mean.shape[1]):
            pdf_dict[x,y] = pdf(x,y)
    for i in xrange(segments.shape[0]):
        _,sb = cv2.threshold(np.copy(segments[i,0])*255, 127, 255, cv2.THRESH_BINARY)
        patches = get_patches(sb)
        if len(patches)==0:
            continue
        sum_pdf_vals = [sum(pdf_dict[x,y] for x,y in p) for p in patches]
        avg_pdf_vals = [sum(pdf_dict[x,y] for x,y in p)/p.shape[0] for p in patches]
        max_sum_pdf = max(sum_pdf_vals)
        for p_idx, p in enumerate(patches):
            if avg_pdf_vals[p_idx] < 0.07 or sum_pdf_vals[p_idx] < max_sum_pdf:
                for x,y in p:
                    seg_binary[i,0,x,y]=0
            else:
                for x,y in p:
                    seg_binary[i,0,x,y]=1
    return seg_binary

def write_outputs(dsets, dest_dir, suffix, w_func=None):
    areas_lines = []
    calc_lines = []
    for dset in dsets:
        if w_func is not None:
            sys_vec, dias_vec = [1, dset.sys_vol], [1, dset.dias_vol]
            calc_lines.append(','.join(['{}']*7).format(dset.name, dset.sys_vol, dset.dias_vol,
                w_func(sys_vec, 0), w_func(sys_vec,1), w_func(dias_vec,2), w_func(dias_vec,3))
                + '\n')
        areas_lines.append('{},{},{},'.format(dset.name, len(dset.slices_ver),len(dset.time)) +
                ','.join(['%.3f'%(c_) for c_ in dset.slocation]) + ',' +
                ','.join(['%.1f'%(c_) for c_ in dset.areas.T.flatten()]) + '\n')
    open(os.path.join(dest_dir, 'areas_map_{}_{}.csv'.format(suffix,
        np.random.randint(1000))), 'w').writelines(areas_lines)
    open(os.path.join(dest_dir, 'areas_map_{}.csv'.format(suffix)), 'w').writelines(areas_lines)
    if w_func is not None:
        open(os.path.join(dest_dir,'calc_map_{}_{}.csv'.format(suffix,np.random.randint(10000))),
                'w').writelines(calc_lines)

def clean_counts(counts, sys_time, dias_time):
    ret = np.copy(counts)
    for s in xrange(counts.shape[0]):
        last_t = t = dias_time
        while (t != sys_time):
            t -= 1
            if t == -1:
                t = counts.shape[1]-1
            ret[s,t] = min(ret[s,t], ret[s, last_t])
            last_t = t
        last_t = t = dias_time
        while (t != sys_time):
            t += 1
            if t == counts.shape[1]:
                t = 0
            ret[s,t] = min(ret[s,t], ret[s, last_t])
            last_t = t
    return ret


# calc_map = { dset_name: ([sys_vector], [dias_vector]) }
# vector is of format [1, calculated_val, (any other variables)]
# e.g. { 1: [1, sys_val, variation, ... ], [1, dias_val, variation, ... ]}
# calculates optimal w (four functions) as linear combination of everything
# in the vector
def optimize_w(calc_vector_map, label_map, dims_to_use = -1, min_w = 1, max_w = 8,
        function=scipy.stats.norm.cdf, verbose=False, above_below=False):
    # slice to fewer dims if specified
    calculated_map = { k:(tuple([v1[:dims_to_use] for v1 in v]) if dims_to_use > 0 else v)
                      for k,v in calc_vector_map.iteritems() if k in label_map }
    lin_constr = lambda x_vec, p_vec: min(max_w, max(min_w, np.dot(x_vec, p_vec)))
    if above_below:
        error_funcs = [lambda a: np.concatenate([calculate_diffs(calc[0][1], label_map[ds][1],
                            lin_constr(calc[0], a), 9, function=function)
                            for ds,calc in calculated_map.iteritems()]),
                      lambda a: np.concatenate([calculate_diffs(calc[0][1], label_map[ds][1], 9,
                            lin_constr(calc[0], a), function=function)
                            for ds,calc in calculated_map.iteritems()]),
                      lambda a: np.concatenate([calculate_diffs(calc[1][1], label_map[ds][0],
                            lin_constr(calc[1], a), 9, function=function)
                            for ds,calc in calculated_map.iteritems()]),
                      lambda a: np.concatenate([calculate_diffs(calc[1][1], label_map[ds][0], 9,
                            lin_constr(calc[1], a), function=function)
                            for ds,calc in calculated_map.iteritems()])]
    else:
        error_funcs = [lambda a: np.concatenate([calculate_diffs(calc[0][1], label_map[ds][1],
                            lin_constr(calc[0], a), lin_constr(calc[0], a), function=function)
                            for ds,calc in calculated_map.iteritems()]),
                      lambda a: np.concatenate([calculate_diffs(calc[1][1], label_map[ds][0],
                            lin_constr(calc[1], a), lin_constr(calc[1], a), function=function)
                            for ds,calc in calculated_map.iteritems()])]
    num_vars = len(calculated_map.values()[0][0])
    guesses = [[5,0.1] + [.01]*(num_vars-2)]*len(error_funcs)
    parms = []
    for func, guess in zip(error_funcs, guesses):
        obj, success = scipy.optimize.leastsq(func, guess)
        parms.append(obj)
        if verbose:
            print obj
    return lambda p, idx: lin_constr(p, parms[idx])

def calculate_submission_values(volume, width_below, width_above, function=sigmoid):
    ret = []
    for i in xrange(600):
        term = function((i-volume)/(width_below if i < volume else width_above))
        ret.append(term)
    return np.array(ret)

def calculate_diffs(calculated, real, width_below, width_above, function=sigmoid):
    calc_vals = calculate_submission_values(calculated, width_below, width_above, function)
    signals = np.array([1 if i > real else 0 for i in range(600)])
    return signals - calc_vals

def calculate_err(calculated, real, width_below, width_above, function=sigmoid):
    diffs = calculate_diffs(calculated, real, width_below, width_above, function)
    return np.square(diffs).mean()

def get_label_map(labels_file):
    labels = np.loadtxt(labels_file, delimiter=',', skiprows=1)
    label_map = {}
    for l in labels:
        label_map[l[0]] = (l[2], l[1])
    return label_map

def get_calc_counts_errors_maps(calc_file, counts_file, labels_file):
    label_map = get_label_map(labels_file)
    calc_map = read_csv(calc_file, header=None)
    calc_map = dict((r[0], (r[1],r[2])) for _,r in calc_map.iterrows())
    counts_map = None
    if counts_file is not None:
        counts_map = open(counts_file, 'r').readlines()
        counts_map = [l.split(',') for l in counts_map]
        counts_map = [[int(st) for st in l] for l in counts_map]
        counts_map = dict((r[0], np.array(r[2:]).reshape((-1,r[1]))) for r in counts_map)
    def error(calc):
        return 0.5*(calculate_err(calc[0], label_map[ds][1], 10, 10) \
                + calculate_err(calc[1], label_map[ds][0], 10, 10))
    errors_map = dict([(ds,error(calc)) for ds,calc in calc_map.iteritems()
        if ds in label_map])
    return calc_map, counts_map, errors_map

def ll_means_stds(counts_list):
    counts_stacked = []
    for c_ in counts_list:
        cm = np.copy(c_)
        cm = (cm*255./cm.max()).astype(np.uint8)
        cm = cm[np.where(cm.sum(axis=1))]
        im = Image.fromarray(cm).resize((30,10), Image.ANTIALIAS)
        resized_counts = np.array(im.getdata(), dtype=np.float32)/255.
        counts_stacked.append(resized_counts)
    counts_stacked = np.array(counts_stacked)
    means = counts_stacked.mean(axis=0)
    stds = counts_stacked.std(axis=0)
    return means, stds

def crop_resize(img, size):
    """crop center and resize"""
    img = img.astype(float) / np.max(img)
    if img.shape[0] < img.shape[1]:
        img = img.T[::-1]
    # we crop image from center
    short_egde = min(img.shape[:2])
    yy = int((img.shape[0] - short_egde) / 2)
    xx = int((img.shape[1] - short_egde) / 2)
    crop_img = img[yy : yy + short_egde, xx : xx + short_egde]
    # resize to 64, 64
    resized_img = transform.resize(crop_img, (size, size))
    resized_img *= 255
    return resized_img.astype("uint8")

def segmenter_data_transform(imb, rotate=None, normalize_pctwise=False):
    if isinstance(imb, tuple) and len(imb) == 2:
        imgs,labels = imb
    else:
        imgs = imb
    # rotate image if training
    if rotate is not None:
        for i in xrange(imgs.shape[0]):
            degrees = float(np.random.randint(rotate[0], rotate[1])) if \
                    isinstance(rotate, tuple) else rotate
            imgs[i,0] = scipy.misc.imrotate(imgs[i,0], degrees, interp='bilinear')
            if isinstance(imb, tuple):
                labels[i,0] = scipy.misc.imrotate(labels[i,0], degrees, interp='bilinear')
    # assume they are square
    sz = c.fcn_img_size
    x,y = np.random.randint(0,imgs.shape[2]-sz,2) if imgs.shape[2] > sz else (0,0)
    imgs = nn.utils.floatX(imgs[:,:, x:x+sz, y:y+sz])/255.
    if not normalize_pctwise:
        pad = imgs.shape[2] // 5
        cut = imgs[:,0,pad:-pad,pad:-pad]
        mu = cut.mean(axis=(1,2)).reshape(imgs.shape[0],1,1,1)
        sigma = cut.std(axis=(1,2)).reshape(imgs.shape[0],1,1,1)
        imgs = (imgs - mu) / sigma
        imgs = np.minimum(3, np.maximum(-3, imgs))
    else:
        pclow, pchigh = normalize_pctwise if isinstance(normalize_pctwise, tuple) else (20,70)
        for i in xrange(imgs.shape[0]):
            pl,ph = np.percentile(imgs[i],(pclow, pchigh))
            imgs[i] = exposure.rescale_intensity(imgs[i], in_range=(pl, ph));
            imgs[i] = 2*imgs[i]/imgs[i].max() - 1.
        # or other rescaling here to approximate ~ N(0,1)
    if isinstance(imb, tuple):
        labels = nn.utils.floatX(labels[:,:, x:x+sz, y:y+sz])
        return imgs, labels
    return imgs

def deconvert(im):
    return ((im-im.min())*255/(im.max()-im.min())).astype(np.uint8)


def z_old_optimize_w(calc_map, label_map):
    calculated_map = dict((k,v) for k,v in calc_map.iteritems() if k in label_map)
    lin_constr = lambda x,a,b: min(20, max(0.5, a*x+b))
    error_funcs = [lambda a: np.concatenate([calculate_diffs(calc[0], label_map[ds][1],
                            lin_constr(calc[0], a[0], a[1]), 9)
                            for ds,calc in calculated_map.iteritems()]),
                  lambda a: np.concatenate([calculate_diffs(calc[0], label_map[ds][1], 9,
                            lin_constr(calc[0], a[0], a[1]))
                            for ds,calc in calculated_map.iteritems()]),
                  lambda a: np.concatenate([calculate_diffs(calc[1], label_map[ds][0],
                            lin_constr(calc[1], a[0], a[1]), 9)
                            for ds,calc in calculated_map.iteritems()]),
                  lambda a: np.concatenate([calculate_diffs(calc[1], label_map[ds][0], 9,
                            lin_constr(calc[1], a[0], a[1]))
                            for ds,calc in calculated_map.iteritems()])]
    guesses = [[0.04656, 4.693],
              [0.03896, -0.4893],
              [0.02458, 1.541],
              [0.03392,0.1355]]
    parms = []
    for func, guess in zip(error_funcs, guesses):
        obj, success = scipy.optimize.leastsq(func, guess)
        parms.append(obj)
    return lambda p, idx: lin_constr(p, parms[idx][0], parms[idx][1])

# given predictions and label map, gives optimal stdev above and below
# for each example
def z_old_optimal_w_funcs(calculated_map, label_map, verbose=False):
    optimal_ws_map = dict((ds,[]) for ds in calculated_map if ds in label_map)
    for ds in [d for d in calculated_map if d in label_map]:
        sys_vol, dias_vol = calculated_map[ds]
        edv, esv = label_map[ds]
        err_func = [lambda x: calculate_err(sys_vol, esv, x, 10),
                   lambda x: calculate_err(sys_vol, esv, 10, x),
                   lambda x: calculate_err(dias_vol, edv, x, 10),
                   lambda x: calculate_err(dias_vol, edv, 10, x)]
        for w_idx in xrange(4):
            min_err = 1000000
            min_w = 0
            for w in xrange(100):
                err = err_func[w_idx](w)
                if err < min_err:
                    min_err = err
                    min_w = w
            optimal_ws_map[ds].append(min_w)
        if verbose and ds % 5 == 0:
            print ds, optimal_ws_map[ds]
    preds_arr = np.empty((len(optimal_ws_map), 6), dtype=np.float32)
    i=0
    for ds in optimal_ws_map:
        preds_arr[i] = np.array([calculated_map[ds][0], calculated_map[ds][1],
                                 min(100,optimal_ws_map[ds][0]),
                                 min(100,optimal_ws_map[ds][1]),
                                 min(100,optimal_ws_map[ds][2]),
                                 min(100,optimal_ws_map[ds][3])])
        i += 1
    degree=1
    wsb1 = np.poly1d(np.polyfit(preds_arr[:,0], preds_arr[:,2], degree))
    wsa1 = np.poly1d(np.polyfit(preds_arr[:,0], preds_arr[:,3], degree))
    wdb1 = np.poly1d(np.polyfit(preds_arr[:,1], preds_arr[:,4], degree))
    wda1 = np.poly1d(np.polyfit(preds_arr[:,1], preds_arr[:,5], degree))
    wsb = lambda x: min(20, max(0, wsb1(x)))
    wsa = lambda x: min(20, max(0, wsa1(x)))
    wdb = lambda x: min(20, max(0, wdb1(x)))
    wda = lambda x: min(20, max(0, wda1(x)))
    return wsb, wsa, wdb, wda
