#------------------------------------------------------------------------------
#
# image_features.py
#
#------------------------------------------------------------------------------

import os, sys, os.path, argparse
import numpy, scipy.ndimage, scipy.signal
import Image, ImageOps

IMAGE_SUFFIX = '.png'

TRAIN_FEATURES_FILE = '../features/image_features_train.csv'
TEST_FEATURES_FILE  = '../features/image_features_test.csv'

TRAIN_DATA_DIR = '../data/spectrogram/all'
TEST_DATA_DIR  = '../data/spectrogram/all'



def filename_seq(directory, tag, suffix, start, end):
    return [directory+'/'+tag+str(i)+suffix for i in range(start, end+1)]

def shrink_array(arr, nbins):
    nrow = nbins
    ncol = len(arr) / nbins
    return arr.reshape((nrow,ncol)).sum(axis=1)

def array_to_features(an_array, tag):
    features = {}
    for i, x in enumerate(an_array):
        features[tag+('%05i' % i)] = x 
    return features

def horiz_exp_mov_avg(img, alpha):
    # Y(t) = (1-alpha)*Y(t-1) + alpha*X(t-1)
    # impulse response = (1-alpha)^t
    assert 0 <= alpha <= 1
    filt_coef_b = [alpha]
    filt_coef_a = [1, -(1-alpha)]
    img_vals = numpy.array(img)
    row_init = numpy.array([[row_vals.mean()] for row_vals in img_vals])
    f_z_init = lambda y_init: scipy.signal.lfiltic(filt_coef_b, filt_coef_a, y_init)
    z_inits  = numpy.array([f_z_init(y_init) for y_init in row_init])
    #print "z_state inits:", z_inits
    img_out, z_state = scipy.signal.lfilter(filt_coef_b, filt_coef_a, img_vals, axis=-1, zi=z_inits)
    return img_out

def image_file_features(infile, cl_options):
    im = Image.open(infile)

    hist_features = {}
    if cl_options.histogram:
        hist_arr = shrink_array(numpy.array(im.histogram()), cl_options.histogram)
        hist_features = array_to_features(hist_arr , 'pixhist_')

    if cl_options.equalize:
        im = ImageOps.grayscale( ImageOps.equalize(im) )

    if cl_options.threshold:
        im = im.point(lambda p: p > cl_options.threshold and 255)

    if cl_options.blur:
        im_blur = scipy.ndimage.gaussian_filter(im, sigma=cl_options.blur)
        im = Image.fromarray(numpy.uint8(im_blur)) # from numpy->Grayscale Image

    if cl_options.horiz_ema:
        # scale to be independent of image size ?????
        im_ema = horiz_exp_mov_avg(im, cl_options.horiz_ema)
        im = Image.fromarray(numpy.uint8(im_ema)) # from numpy->Grayscale Image

    if cl_options.thumb_size:
        thumb_size = (cl_options.thumb_size, cl_options.thumb_size)
        im.thumbnail(thumb_size, Image.ANTIALIAS)

    if cl_options.thumb_dir:
        basename = os.path.basename(infile).split('.')[0]
        thumb_file = cl_options.thumb_dir + '/' + basename + '.png'
        im.save(thumb_file, "png")

    pix_features = {}
    if cl_options.pixels:
        pix_values = im.getdata() # returns a 1-D/flattened sequence of pixel values
        pix_features = array_to_features(pix_values, 'pix_')

    return dict(pix_features.items() + hist_features.items()) 


def write_features(feature_outfile, infiles, cl_options):
    fout = open(feature_outfile,'w')
    wrote_header = False
    print
    for infile in infiles:
        print "\rprocessing:", infile,
        features = {}
        features['clip_name'] = os.path.basename(infile)
        
        # read image & create features
        image_features = image_file_features(infile, cl_options)
        features.update(image_features)

        if not wrote_header:
            header = ','.join([tag for tag in sorted(features)])
            fout.write(header+'\n')
            wrote_header = True

        outline = ','.join([str(features[tag]) for tag in sorted(features)])
        fout.write(outline+'\n')
    fout.close()
    print '\nWrote features to:', feature_outfile

def parseCommandLine():
    parser = argparse.ArgumentParser('')
    parser.add_argument('--pixels',     action='store_true', help='make image pixel value features')
    parser.add_argument('--thumb_size', type=int, help='thumbnail image size in pixels (both x & y) ')
    parser.add_argument('--thumb_dir',  type=str, help='dir to write image thumbnails to')
    parser.add_argument('--equalize',   action='store_true', help='equalize pixel value histogram')
    parser.add_argument('--threshold',  type=int,   help='int value for image thresholding')
    parser.add_argument('--blur',       type=float, help='sigma value for image Gaussian blurring')
    parser.add_argument('--horiz_ema',  type=float, help='exponential moving average time constant')
    parser.add_argument('--histogram',  type=int,   help='make pixel value histogram using N bins')
    options = parser.parse_args()
    return options 

def echoOptions(cl):
    print "Parameters being used:\n"
    cl_vars = vars(cl)
    for cl_var in cl_vars:
        print "  ",cl_var,"--> [",cl_vars[cl_var],"]"
    print 


def main():
    
    print "\n*** Spectrogram Image Features for Whale Detection Challenge on Kaggle ***\n"

    cl_options= parseCommandLine()
    echoOptions(cl_options)

    train_filenames = filename_seq(TRAIN_DATA_DIR, 'train', IMAGE_SUFFIX, 1, 30000)
    test_filenames  = filename_seq(TEST_DATA_DIR,  'test',  IMAGE_SUFFIX, 1, 54503)

    print 'creating image features'
    write_features(TRAIN_FEATURES_FILE, train_filenames, cl_options)
    write_features(TEST_FEATURES_FILE,  test_filenames,  cl_options)

    print '\nDone\n'


if __name__ == '__main__':
    main()

