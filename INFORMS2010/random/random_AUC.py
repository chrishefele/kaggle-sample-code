# creates kFold subsets  of about 200 points each

from numpy import array
import numpy, numpy.random
import sys
from scikits.learn.metrics import roc, auc
from scikits.learn.cross_val import KFold

# =============================================================================
TESTING_FILE  = "/home/chefele/INFORMS2010/data/ResultData.csv"
TRAINING_FILE = "/home/chefele/INFORMS2010/data/TrainingData.csv"

def readDataFile(filename):
    print "Reading:", filename
    sys.stdout.flush()
    fin = open(filename,"r")   
    titlesLine = fin.readline()
    inTitles = [inTitle.strip() for inTitle in titlesLine.split(",")] 
    inData={}
    for inTitle in inTitles:
        inData[inTitle]=[]
    for dataLine in fin.readlines():
        inDatums = [datum.strip() for datum in dataLine.split(",")] 
        for inTitle, inDatum in zip(inTitles, inDatums):
             inData[inTitle].append(inDatum)
    print "Finished reading:", filename
    return inData

def calcAUC(targetData):
    yData = targetData 
    probas = numpy.random.random((len(targetData)))
    FPR, TPR, thresholds = roc(yData, probas) 
    roc_auc = auc(FPR, TPR)
    return roc_auc

def main():
    theData = readDataFile(TRAINING_FILE)
    targetData = numpy.array([float(targetVarStr) for targetVarStr in theData["TargetVariable"]])
    samples = len(targetData)
    folds =  23  # yields about 250 pts per fold
    auclist=[]
    for train, test in KFold(samples, folds):
        auc = calcAUC(targetData[test])
        print "AUC:", auc, "Pts:", len(targetData[test])
        auclist.append(auc)
    aucarr = numpy.array(auclist)
    print "Mean:", aucarr.mean(), "Std:", aucarr.std()

main()

