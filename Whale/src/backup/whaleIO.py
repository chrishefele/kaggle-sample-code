# -----------------------------------------------------------------------------
# whaleIO.py 
#
# IO routines for audio clips used in the Kaggle Whale Detection Challenge
#
# CJH 2/12/2013
# -----------------------------------------------------------------------------

import aifc 
import wave
import numpy
import struct
import scipy.signal

# -----------------------------------------------------------------------------

# Audio file parameters
NCHANNELS   = 1    # 1=mono, 2=stereo
SAMPWIDTH   = 2    # bytes/sample
FRAMERATE   = 2000 # Hz
NFRAMES     = 4000 
COMPTYPE    = 'NONE'
COMPTYPETAG = 'no compression'

# Maximum signal amplitude (assuming short int)
SAMPBITS    = 8*SAMPWIDTH
SIG_SCALE   = pow(2, SAMPBITS-1) -1 # max value must not overflow 

TRAIN_ANSWERS   = '../download/data/train.csv' # class labels

# -----------------------------------------------------------------------------

def read_signal_response():
    fin = open(TRAIN_ANSWERS, 'r')
    fin.readline()  # skip header line
    signal_response = {}
    for line in fin:
        tokens = line.split(',')
        filename    =     tokens[0]
        whale_heard = int(tokens[1])
        signal_response[filename] = whale_heard
    return signal_response

def read_signal(filename, filetype, print_stats=True, normalize=False):
    if filetype == 'aiff':
        fin = aifc.open(filename, 'r')
        need_byte_swap = True
    elif filetype == 'wav':
        fin = wave.open(filename, 'r')
        need_byte_swap = False
    else:
        raise RuntimeError, 'filetype must be wav or aiff'
        
    nframes = fin.getnframes()
    frames  = fin.readframes(nframes)
    fin.close()
    signal  = numpy.fromstring(frames, numpy.short)
    if need_byte_swap:
        signal = signal.byteswap()
    signal  = numpy.array(signal, dtype=numpy.float)
    rms     = numpy.sqrt((signal*signal).mean())

    if normalize:
        signal = signal / rms
    if print_stats:
        print 'file:', filename, 'frames:', nframes, 'rms:', rms

    return signal


def signal_string(signal):
       # converts an array of short ints to a binary string
       return ''.join([wave.struct.pack('h', sample) for sample in signal])


def write_signal(sig, filename, filetype, print_stats=True):
    if filetype == 'aiff':
        fout = aifc.open(filename, 'w')
        fout.aiff()
        need_byte_swap = True  # endian-ness issue
    elif filetype == 'wav':
        fout = wave.open(filename, 'w')
        need_byte_swap = False 
    else:   
        raise RuntimeError, 'filetype must be wav or aiff'
        
    fout.setnchannels(NCHANNELS)
    fout.setsampwidth(SAMPWIDTH)    # Set the sample width to n bytes.
    fout.setframerate(FRAMERATE) # Set the frame rate to n.
    fout.setnframes(NFRAMES)
    fout.setcomptype(COMPTYPE, COMPTYPETAG)

    sig_scaled = numpy.around( sig/(abs(sig).max()) * SIG_SCALE)
    sig_out = numpy.short(sig_scaled)
    if need_byte_swap:
        sig_out = sig_out.byteswap() 
    sig_str = signal_string(sig_out)
    fout.writeframes(sig_str)
    fout.close()
    if print_stats:
        print "wrote:", filename


def TEST():
    t = numpy.array(range(NFRAMES))/float(FRAMERATE)
    f0 = 307
    f1 = 2*f0
    t1 = t[-1]
    signal = SIG_SCALE * scipy.signal.chirp(t,f0,t1,f1,method='linear')

    write_signal(signal,   'whaleIO_TEST_1.wav',  'wav')
    write_signal(signal,   'whaleIO_TEST_1.aiff', 'aiff')
    sig_wav  = read_signal('whaleIO_TEST_1.wav',  'wav')
    sig_aiff = read_signal('whaleIO_TEST_1.aiff', 'aiff')
    write_signal(sig_wav,  'whaleIO_TEST_2.wav',  'wav')
    write_signal(sig_aiff, 'whaleIO_TEST_2.aiff', 'aiff')

if __name__=='__main__':
    print read_signal_response()
    TEST()
