import os
import stat
import hashlib
import whaleIO
import numpy
import math

#------------------------------------------------------------------------------

AUDIO_SUFFIX = '.aiff'

TRAIN_FEATURES_FILE = '../features/file_features_train.csv'
TEST_FEATURES_FILE  = '../features/file_features_test.csv'

TRAIN_DATA_DIR = '../download/data/train'
TEST_DATA_DIR  = '../download/data/test'

FILE_ID_BINS = 100

#------------------------------------------------------------------------------

def isOwnerExecutable(filepath):
    st = os.stat(filepath)
    return bool(st.st_mode & stat.S_IXUSR)

def hashfile(filepath):
    sha1 = hashlib.sha1()
    f = open(filepath, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()

def filename_seq(directory, tag, suffix, start, end):
    return [directory+'/'+tag+str(i)+suffix for i in range(start, end+1)]

def rms(a):
    return math.sqrt((a*a).mean())

def abs_dB(x):
    return math.log10(abs(x))

def file_signal_stats(filepath):
    features = {}
    sig = whaleIO.read_signal(filepath, 'aiff', print_stats=False, normalize=False)

    features['sig_max']     = sig.max()
    features['sig_min']     = sig.min()
    features['sig_mean']    = sig.mean()

    features['sig_max_absdb'] = abs_dB(sig.max())
    features['sig_min_absdb'] = abs_dB(sig.min())

    features['sig_rms']     = rms(sig)
    features['sig_rms_db']  = abs_dB(rms(sig))

    deltas = numpy.diff(sig)
    features['sig_delta_rms']    = rms(deltas)
    features['sig_delta_rms_db'] = abs_dB(rms(deltas))
    features['sig_rough_freq']   = rms(deltas) / rms(sig)
    return features

def write_file_features(feature_outfile, infiles, hash_files={} ):

    fout = open(feature_outfile,'w')
    wrote_header = False
    hash_files = {}

    print
    for infile in infiles:
        print "\rprocessing:", infile,
        features = {}
        features['clip_name'] = os.path.basename(infile)
        features['clip_ownerexecutable'] = 1 if isOwnerExecutable(infile) else 0
        features.update(file_signal_stats(infile)) 

        # duplicate file flag
        h = hashfile(infile)
        if h not in hash_files:
            features['duplicate'] = 0
            hash_files[h] = [infile]
        else:
            features['duplicate'] = 1
            hash_files[h].append(infile)

        # file id bins - binary flags for if a file's id# is in each bin
        filename_digits = [c for c in os.path.basename(infile) if c in '0123456789']
        file_id = int(''.join(filename_digits))
        for i in range(1,FILE_ID_BINS+1):
            features['fileid_bin_%03i' % i] = 0
        fileid_bin = int(FILE_ID_BINS) * int(file_id-1) / len(infiles) + 1
        features['fileid_bin_%03i' % fileid_bin] = 1

        if not wrote_header:
            header = ','.join([tag for tag in sorted(features)])
            fout.write(header+'\n')
            wrote_header = True

        outline = ','.join([str(features[tag]) for tag in sorted(features)])
        fout.write(outline+'\n')
    fout.close()
    print '\nWrote features to:', feature_outfile
    return hash_files


def main():

    print '\n*** File Features (permissions, ID) for Whale Detection Challenge ***\n'

    train_filenames = filename_seq(TRAIN_DATA_DIR, 'train', '.aiff', 1, 30000)
    test_filenames  = filename_seq(TEST_DATA_DIR,  'test',  '.aiff', 1, 54503)

    print 'Creating file features\n'
    hash_files = write_file_features(TRAIN_FEATURES_FILE, train_filenames, hash_files={} )
    _          = write_file_features(TEST_FEATURES_FILE,  test_filenames,  hash_files=hash_files)

    print '\nDone\n'


if __name__ == '__main__':
    main()

