
import cv2
import sys
import collections

DIR_TRAIN = "../download/train/"
DIR_TEST  = "../download/test/"
#DIR_SRC = DIR_TRAIN # TODO 
DIR_SRC = DIR_TEST # TODO 
SET_MAX = 344

setids_all = range(1, SET_MAX+1)
setids_train = [ \
    4, 5, 10, 12, 16, 20, 21, 25, 29, 31, 35, 43, 44, 
    50, 53, 57, 58, 59, 69, 78, 79, 94, 97, 107, 112, 131, 
    137, 143, 144, 158, 160, 165, 171, 173, 175, 176, 178,
    190, 194, 201, 203, 205, 211, 217, 218, 220, 223, 224,
    229, 239, 241, 251, 252, 255, 257, 264, 268, 274, 277,
    279, 285, 297, 298, 301, 303, 307, 311, 327, 340, 342 ]
setids_test = list(sorted( set(setids_all) - set(setids_train) ))


def find_orig_fileid(setid):

    results = collections.defaultdict(list)
    for fileid in (1,2,3,4,5):
        file_in = "set" + str(setid) + "_" + str(fileid) + ".tif"
        img = cv2.imread(DIR_SRC + file_in)
        for chan, chan_c in enumerate(('B','G','R')): 
            hist  = cv2.calcHist([img], [chan], None, [256], [0,256])
            ihist = hist.flatten().astype(int)
            zeros = sum(ihist == 0)
            results[chan_c].append(zeros)
    orig_fileids = []
    for chan_c in results.keys():
        chan_result = results[chan_c]
        orig_fileid = chan_result.index(min(chan_result)) + 1
        orig_fileids.append(orig_fileid)
    
    assert len(set(orig_fileids)) == 1
    return orig_fileids[0]


def main():

    fileid_hits = collections.defaultdict(int)

    #for setid in setids_train:  # TODO 
    for setid in setids_test:  # TODO 

        orig_fileid = find_orig_fileid(setid)

        print 'set %3i orig_fileid %i' % (setid, orig_fileid), 
        fileid_hits[orig_fileid] += 1
        print "fileid:hits", fileid_hits

    print "\nfileid:hits", fileid_hits


if __name__ == '__main__':
    main()

#imsave(f_out, im)

