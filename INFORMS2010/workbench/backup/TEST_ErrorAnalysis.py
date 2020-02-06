import ProvidedData
from Transforms import *
from Prediction import *
import scikits.learn.logistic

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
timestamps = pd.getTimestamps()

 
dataDescription = [ [ normCenter, timeShiftVars, normCenter, floatDataGetter ] ]
# dataDescription = [ [ normCenter, floatDataGetter ] ]

print "Transforming data"
transformedData = transformData(dataDescription)
# print transformedData
print "Now testing predictions"

print "Predicting...using KFold"
classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')
preds = kFoldPrediction( transformedData, targetVariable, classifier(0.01) )
print "Finished predicting"

print "AUC:", AUC(targetVariable, preds)

fracTimestamps = timestamps - numpy.fix(timestamps)
before3pmMask = fracTimestamps < 0.625 # 0.625 = 3pm
print "AUC_before3PM:", AUC(targetVariable[before3pmMask],preds[before3pmMask])

fracTimestamps = timestamps - numpy.fix(timestamps) 
trainMask = numpy.isfinite(targetVariable)
sumActuals={}
sumProbs={}
for fts, tv, pred in zip(fracTimestamps[trainMask], targetVariable[trainMask], preds[trainMask]):
    if fts in sumActuals and fts in sumProbs:
        sumActuals[fts] = sumActuals[fts] + tv
        sumProbs[fts] = sumProbs[fts] + pred
    else:
        sumActuals[fts] = tv
        sumProbs[fts] = pred
fractionalTimestamps = sumActuals.keys()
for fts in sorted(fractionalTimestamps):
    print "Time:",fts,"Actual#1s:",sumActuals[fts],"Predicted#1s:",sumProbs[fts]


     

