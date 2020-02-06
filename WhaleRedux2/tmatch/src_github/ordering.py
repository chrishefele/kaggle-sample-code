""" ordering.py: generate ordering feature
"""
import globalConst
import numpy as np
import pylab as pl
import pandas as pd
import fileio


def writeToFile(out,outname='out.csv',outdir=''):
    """"""
    file = open(outdir+outname,'w')
    np.savetxt(file,out,delimiter=',')
    file.close()
    print "Wrote file:", outdir+outname

def orderMetric(truth,n):
    """Calculate the average excluding the center"""
    pad_ = np.zeros(2*n+truth.size)
    pad_[n:truth.size+n] = truth.copy()
    return np.array([(np.sum(pad_[(i-n):i+n]) - pad_[i])/(2*n-1) for i in range(n,pad_.size-n)])

def main():
    #baseDir = '/home/nick/whale/'
    baseDir = globalConst.BASE_DIR
    dataDir = baseDir+'data/'
    corDir  = baseDir+'moby/'

    # Open up the train file
    train = fileio.TrainData(dataDir+'train.csv',dataDir+'train/')
    t_    = pd.read_csv( corDir+'trainPredictions.csv')
    order32_ = orderMetric(t_.label,32)
    order64_ = orderMetric(t_.label,64)

    # Reorder the data
    reorder32 = order32_.copy()
    reorder64 = order64_.copy()

    # NOTE disabled reordering below, because modified genTrainMetrics 
    # now writes in chronological order, not 'reordered' as below. 
    """
    k = 0
    for i in xrange(train.numH1):
        j = int(train.h1[i].split('.')[0][5:]) - 1
        reorder32[k] = order32_[j] 
        reorder64[k] = order64_[j] 
        k += 1
    for i in xrange(train.numH0):
        j = int(train.h0[i].split('.')[0][5:]) - 1
        reorder32[k] = order32_[j] 
        reorder64[k] = order64_[j] 
        k += 1
    """

    writeToFile(reorder32, 'corr32.csv', outdir=corDir)
    writeToFile(reorder64, 'corr64.csv', outdir=corDir)

    """
    # There are 84503 samples
    trainSize = globalConst.N_TRAIN
    testSize  = globalConst.N_TEST
    size_ = trainSize + testSize
    tt_ = size_*2. # since these are 2 second clips
    xs_ = np.linspace(0,tt_,testSize)
    xt_ = np.linspace(0,tt_,trainSize)
    test32_ = np.interp(xs_,xt_,order32_)
    test64_ = np.interp(xs_,xt_,order64_)
    """
    t_ = pd.read_csv(corDir+'testPredictions.csv')
    if 'label' in t_.columns:  # similar to train.csv 
        test32_ = orderMetric(t_.label,32)
        test64_ = orderMetric(t_.label,64)
    elif 'probability' in t_.columns:   # similar to submissions file 
        test32_ = orderMetric(t_.probability,32)
        test64_ = orderMetric(t_.probability,64)
    else:
        raise RuntimeError, "label or probability not found in testPredictions.csv"

    writeToFile(test32_, 'testCorr32.csv', outdir=corDir)
    writeToFile(test64_, 'testCorr64.csv', outdir=corDir)

if __name__=="__main__":
    main()
