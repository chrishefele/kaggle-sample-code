
import glob
import os.path 
import cv2
import numpy as np 
import collections
import matplotlib
import scipy.spatial.distance
import itertools
import matplotlib.pyplot as plt 
import matplotlib.animation as animation

IMAGE_DIR        = '../download/train/'
TILE_MIN_SIDE    = 50     # pixels; see tile_features()

def get_image(f):
    # Read image file 
    img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
    # print 'Read:', f, "with shape:", img.shape
    return img

def get_images(patient=None):
    if patient: 
        f_path = IMAGE_DIR + '%i_*.tif' % patient 
    else:
        f_path = IMAGE_DIR + '*.tif' 
    f_ultrasounds = [f for f in glob.glob(f_path) if 'mask' not in f]
    images = {f:get_image(f) for f in sorted(f_ultrasounds)}
    return images

def to_mask_path(f_image):
    # Convert an image file path into a corresponding mask file path 
    dirname, basename = os.path.split(f_image)
    maskname = basename.replace(".tif", "_mask.tif")
    return os.path.join(dirname, maskname)

def not_blank_mask(f_image):
    return get_image(to_mask_path(f_image)).flatten().sum() > 0 

def not_blank_masks(f_images):
    return { f: not_blank_mask(f) for f in sorted(f_images)}

def image_features(img):
    return tile_features(img)   # a tile is just an image...

def tile_features(tile, tile_min_side = TILE_MIN_SIDE):
    # Recursively split a tile (image) into quadrants, down to a minimum 
    # tile size, then return flat array of the mean brightness in those tiles.
    tile_x, tile_y = tile.shape
    mid_x = tile_x / 2
    mid_y = tile_y / 2
    if (mid_x < tile_min_side) or (mid_y < tile_min_side):
        return np.array([tile.mean()]) # hit minimum tile size
    else:
        tiles = [ tile[:mid_x, :mid_y ], tile[mid_x:, :mid_y ], 
                  tile[:mid_x , mid_y:], tile[mid_x:,  mid_y:] ] 
        features = [tile_features(t) for t in tiles]
        return np.array(features).flatten()

def feature_dist(feats_0, feats_1):
    # Definition of the distance metric between image features
    return scipy.spatial.distance.euclidean(feats_0, feats_1)

def feature_dists(features):
    # Calculate the distance between all pairs of images (using their features)
    dists = collections.defaultdict(list)
    f_imgs = features.keys()
    for f_img0 in f_imgs:
        print 'calculating dists for:', f_img0
        for f_img1 in f_imgs:
            if f_img0 == f_img1: 
                continue
            dist = feature_dist(features[f_img0], features[f_img1])
            dists[f_img0].append( (dist, f_img1) )
        dists[f_img0].sort()
    return dists


def main(patient):

    print "Reading images"
    images       = get_images(patient=patient)
    not_blank    = not_blank_masks(images)

    print "Calculating features"
    features     = { f : image_features(images[f]) for f in images }

    print "Calculating distances"
    dists        = feature_dists(features)

    print "Tabulating results"
    dists_nerve = dists_no_nerve = 0
    n_nerve     = n_no_nerve     = 0 
    for f1 in dists:
        dists_arr = np.array([d for d, f2 in dists[f1]])
        if not_blank[f1]:
            dists_nerve    += dists_arr
            n_nerve += 1
        else:
            dists_no_nerve += dists_arr
            n_no_nerve += 1
     
    print "RESULTS"
    print "n_nerve:", n_nerve
    print "nerve   :", dists_nerve/n_nerve
    print "n_no_nerve:", n_no_nerve
    print "no_nerve:", dists_no_nerve/n_no_nerve
    print
    ratio = (dists_nerve/n_nerve) / (dists_no_nerve/n_no_nerve)
    for n, r in enumerate(ratio):
        print "%6i,%8.5f" % (n, r)


main(patient=None)
        


