import sys
sys.path.append("/home/chefele/INFORMS2010/workbench/source")
import ProvidedData
from Transforms import *
from InputOutput import loadPredictionsFile
from Prediction import AUC
import numpy, numpy.random

SAMPLE_FRACTION = 0.10 
N_TARGET_PREDS = 2539
N_BOOT_SAMPLES = 1000

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
timestamps = pd.getTimestamps()
trainMask = numpy.isfinite(targetVariable) 

preds1fname = sys.argv[1]
preds2fname = sys.argv[2]
preds1dict = loadPredictionsFile(preds1fname)
preds2dict = loadPredictionsFile(preds2fname)
preds1 = preds1dict[ preds1dict.keys()[0] ] 
preds2 = preds2dict[ preds2dict.keys()[0] ]


tvTrain = targetVariable[trainMask][1:N_TARGET_PREDS]
preds1Train = preds1[trainMask][1:N_TARGET_PREDS]
preds2Train = preds2[trainMask][1:N_TARGET_PREDS]

print "FULL_AUC1:",AUC(tvTrain,preds1Train)
print "FULL_AUC2:",AUC(tvTrain,preds2Train)
print "DELTA:", AUC(tvTrain,preds1Train) - AUC(tvTrain,preds2Train)

diffs = []
for i in xrange(N_BOOT_SAMPLES):
    bootmask = numpy.random.random(len(tvTrain)) < SAMPLE_FRACTION
    tvBoot = tvTrain[bootmask]
    preds1Boot = preds1Train[bootmask]
    preds2Boot = preds2Train[bootmask]
    auc1 = AUC(tvBoot, preds1Boot)
    auc2 = AUC(tvBoot, preds2Boot)
    print "Sample:", auc1, auc2, auc1-auc2 
    diffs.append(auc1-auc2)

adiffs = numpy.array(diffs)
print "Bootstrapped:", N_BOOT_SAMPLES, "samples; Mean:", adiffs.mean(), "Std:", adiffs.std()





