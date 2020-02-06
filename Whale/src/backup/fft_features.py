#------------------------------------------------------------------------------
#
# fft_features.py
#
#------------------------------------------------------------------------------

from whaleIO import read_signal, write_signal
from whaleIO import FRAMERATE, NFRAMES
import scipy.signal
import scipy.fftpack
import numpy 
import os.path
import pylab

#------------------------------------------------------------------------------

AUDIO_SUFFIX = '.aiff'

TRAIN_FEATURES_FILE = '../features/fft_features_train.csv'
TEST_FEATURES_FILE  = '../features/fft_features_test.csv'

TRAIN_DATA_DIR = '../download/data/train'
TEST_DATA_DIR  = '../download/data/test'

PLOT_DIR = '../data/fft/all'

NPTS_PSD    = 200 # must be even sub-multiple of 4000/2=2000 samples
NPTS_PSD_SQ = 200

#------------------------------------------------------------------------------

def filename_seq(directory, tag, suffix, start, end):
    return [directory+'/'+tag+str(i)+suffix for i in range(start, end+1)]

def array_to_features(an_array, tag):
    features = {}
    for i, x in enumerate(an_array):
        features[tag+('%04i' % i)] = x 
    return features

def shrink_array(arr, nbins):
    nrow = nbins
    ncol = len(arr) / nbins 
    return arr.reshape((nrow,ncol)).mean(axis=1)

def sig_to_shrunk_psd(sig, npts):
    fft_sig = scipy.fftpack.fft(sig)
    fft_sig = fft_sig[range(len(fft_sig)/2)]
    psd_sig = numpy.log10( numpy.abs(fft_sig) * numpy.abs(fft_sig) )
    return shrink_array(psd_sig, npts)

def write_fft_features(feature_outfile, audio_infiles):
    fout = open(feature_outfile,'w')
    wrote_header = False
    print
    for audio_infile in audio_infiles:
        print "\rprocessing:", audio_infile,
        features = {}
        features['clip_name'] = os.path.basename(audio_infile)

        sig    = read_signal(audio_infile, 'aiff', print_stats=False, normalize=False) 
        sig_sq = sig*sig
        psd_shrunk    = sig_to_shrunk_psd(sig,    NPTS_PSD   )
        psd_shrunk_sq = sig_to_shrunk_psd(sig_sq, NPTS_PSD_SQ)

        features.update( array_to_features(psd_shrunk,    'psd_'    ))
        features.update( array_to_features(psd_shrunk_sq, 'psd_sq_' ))

        basename = os.path.basename(audio_infile).split('.')[0]
        # write_psd_plot(psd_shrunk,    PLOT_DIR + '/psd-'   +basename+'.png')
        # write_psd_plot(psd_shrunk_sq, PLOT_DIR + '/psd_sq-'+basename+'.png')

        if not wrote_header:
            header = ','.join([tag for tag in sorted(features)])
            fout.write(header+'\n')
            wrote_header = True

        outline = ','.join([str(features[tag]) for tag in sorted(features)])
        fout.write(outline+'\n')
    fout.close()
    print '\nWrote FFT features to:', feature_outfile

def write_psd_plot(psd, fout):
    xs = range(len(psd))
    ys = psd 
    pylab.clf() # clear figure
    pylab.xlabel("relative frequency")
    pylab.ylabel("PSD (dB)")
    # colors: 'b' (default), 'r' red, 'g' green
    pylab.plot(xs, ys, 'b')
    # save the plot as a (PNG) image file (optional)
    pylab.savefig(fout)

def main():
    print '\n*** FFT Features for Whale Detection Challenge ***\n'

    train_filenames = filename_seq(TRAIN_DATA_DIR, 'train', '.aiff', 1, 30000)
    test_filenames  = filename_seq(TEST_DATA_DIR,  'test',  '.aiff', 1, 54503)

    print 'Creating FFT features\n'
    write_fft_features(TRAIN_FEATURES_FILE, train_filenames)
    write_fft_features(TEST_FEATURES_FILE,  test_filenames)

    print '\nDone\n'


if __name__ == '__main__':
    main()

