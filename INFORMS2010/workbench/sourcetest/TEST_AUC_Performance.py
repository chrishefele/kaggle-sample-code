from scikits.learn.metrics import roc, auc
import scikits
import numpy
import numpy.random
import time


def AUC(targetVariable, allPredictions):
    trainMask = numpy.isfinite(targetVariable)
    targetVariableTrainOnly = targetVariable[trainMask]
    predictionsTrainOnly = allPredictions[trainMask]
    FPR, TPR, thresholds = roc(targetVariableTrainOnly, predictionsTrainOnly) 
    roc_auc = auc(FPR, TPR)
    return roc_auc

MAX = 5923
preds0  = numpy.random.random(MAX)
target0 = numpy.random.randint(0,2,MAX)
for n in range(1,10):
    numVals = MAX/n
    preds = preds0[:numVals]
    target = target0[:numVals]
    t0 = time.time()
    roc_auc = AUC(target, preds)
    t1 = time.time()
    print "Pts:",numVals,"AUC:", roc_auc, "Secs:",t1-t0

for decpts in range(0,10):
    numVals = MAX
    preds = preds0[:numVals]
    target = target0[:numVals]
    t0 = time.time()
    roc_auc = AUC(target, numpy.round(preds,decimals=decpts))
    t1 = time.time()
    print "Decpts:",decpts,"AUC:", roc_auc, "Secs:",t1-t0
