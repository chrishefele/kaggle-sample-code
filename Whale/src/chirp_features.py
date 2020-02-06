#------------------------------------------------------------------------------
#
# chirp_features.py
#
#------------------------------------------------------------------------------

from whaleIO import read_signal, write_signal
from whaleIO import FRAMERATE, NFRAMES
import scipy.signal
import numpy 
import os.path

#------------------------------------------------------------------------------

AUDIO_SUFFIX = '.aiff'

TRAIN_FEATURES_FILE = '../features/chirp_features_train.csv'
TEST_FEATURES_FILE  = '../features/chirp_features_test.csv'

TRAIN_DATA_DIR = '../download/data/train'
TEST_DATA_DIR  = '../download/data/test'

CHIRP_DIR      = '../data/chirps' 

CHIRP_F_LO   =  50 # Hz (for all)
CHIRP_F_HI   = 350 
CHIRP_F_STEP =  10 

CHIRP_T0  = 0.5  # seconds into clip to start chirp
CHIRP_T1  = 1.25

#CHIRP_METHOD = 'linear'
CHIRP_METHOD = 'logarithmic'


#------------------------------------------------------------------------------

def get_chirps(f0_list, f1_list, chirp_t0=0.5, chirp_t1=1.25, chirp_method='linear'):

    chirp_duration      = float(chirp_t1 - chirp_t0)
    n_chirp_frames      = int(round(chirp_duration * FRAMERATE))
    n_prechirp_frames   = int(round(      chirp_t0 * FRAMERATE))
    n_postchirp_frames  = NFRAMES - n_chirp_frames - n_prechirp_frames
    prechirp  = numpy.zeros(n_prechirp_frames) 
    postchirp = numpy.zeros(n_postchirp_frames) 

    chirps = []
    t1 = chirp_duration
    t  = numpy.array(range(n_chirp_frames)) / float(FRAMERATE)
    window = scipy.signal.hann(n_chirp_frames)
    for f0 in f0_list:
        for f1 in f1_list:
            tag = 'chirp_f%03i_f%03i' % (f0, f1)
            chirp00 = scipy.signal.chirp(t,f0,t1,f1, method=chirp_method, phi= 0)
            chirp90 = scipy.signal.chirp(t,f0,t1,f1, method=chirp_method, phi=90)
            sig00 = numpy.concatenate((prechirp, chirp00*window, postchirp))
            sig90 = numpy.concatenate((prechirp, chirp90*window, postchirp))
            chirps.append( (tag,sig00,sig90) )
    return chirps


def filename_seq(directory, tag, suffix, start, end):
    return [directory+'/'+tag+str(i)+suffix for i in range(start, end+1)]

def L2_norm(signal):
    return numpy.sqrt( (signal*signal).sum() ) 

def write_chirp_features(feature_outfile, audio_infiles, chirps):

    fout = open(feature_outfile,'w')
    wrote_header = False

    print
    for audio_infile in audio_infiles:
        print "\rprocessing:", audio_infile,
        sig = read_signal(audio_infile, 'aiff', print_stats=False, normalize=False) 
        features = {}

        features['clip_name'] = os.path.basename(audio_infile)

        for chirp_tag, chirp_sig00, chirp_sig90 in chirps:
            dotprod00 = (sig * chirp_sig00).sum()   
            dotprod90 = (sig * chirp_sig90).sum()
            pwr = numpy.sqrt(dotprod00*dotprod00 + dotprod90*dotprod90)
            features[chirp_tag] = numpy.log(pwr)  

        if not wrote_header:
            header = ','.join([chirp_tag for chirp_tag in sorted(features)])
            fout.write(header+'\n')
            wrote_header = True

        outline = ','.join([str(features[chirp_tag]) for chirp_tag in sorted(features)])
        fout.write(outline+'\n')
    fout.close()
    print '\nWrote chirp features to:', feature_outfile


def write_chirps(chirps, chirp_dir):
    for chirp_tag, chirp_sig00, chirp_sig90 in chirps:
        filetype = 'aiff'
        filename00 = chirp_dir + '/' + chirp_tag + '_p00.' + filetype
        filename90 = chirp_dir + '/' + chirp_tag + '_p90.' + filetype
        write_signal(chirp_sig00, filename00, filetype, print_stats=False)
        write_signal(chirp_sig90, filename90, filetype, print_stats=False)


def main():

    print '\n*** Chirp Features for Whale Detection Challenge ***\n'

    train_filenames = filename_seq(TRAIN_DATA_DIR, 'train', '.aiff', 1, 30000)
    test_filenames  = filename_seq(TEST_DATA_DIR,  'test',  '.aiff', 1, 54503)

    print 'Generating chirp signals'
    f0_list = range(CHIRP_F_LO, CHIRP_F_HI, CHIRP_F_STEP)
    f1_list = range(CHIRP_F_LO, CHIRP_F_HI, CHIRP_F_STEP)
    chirps = get_chirps( f0_list, f1_list, \
                         chirp_t0=CHIRP_T0, chirp_t1=CHIRP_T1, chirp_method=CHIRP_METHOD )

    print 'Writing',len(chirps),'chirp audio clips to:', CHIRP_DIR
    write_chirps(chirps, CHIRP_DIR)

    print 'Creating chirp features\n'
    write_chirp_features(TRAIN_FEATURES_FILE, train_filenames, chirps)
    write_chirp_features(TEST_FEATURES_FILE,  test_filenames,  chirps)

    print '\nDone\n'


if __name__ == '__main__':
    main()

