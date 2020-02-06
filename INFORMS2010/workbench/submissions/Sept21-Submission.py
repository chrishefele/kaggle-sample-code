import sys
sys.path.append("/home/chefele/INFORMS2010/workbench/source")

import ProvidedData
from Transforms import *
from Prediction import *
from Optimize import * 
import scikits.learn.logistic
import scikits.learn.svm
import itertools

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
timestamps = pd.getTimestamps()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
intDataGetter = makeGetCategoricalVars(pd.getIntData)
var74Selector = makeSelectVars("Variable74_LASTLASTRETURN")
getTimeOfDayMeanTargetVar = makeGetTimeOfDayMeanTargetVar(timestamps, targetVariable)

dayCenter       = makeDayCenter(timestamps) # hurts a lot
periodCenter    = makePeriodCenter(timestamps) # hurts a little 
dayNorm         = makeDayNorm(timestamps)   # hurts a lot 
periodNorm      = makePeriodNorm(timestamps)  # WORKS VERY WELL by itself or w normCenter


dataDescription = [[ percentileVars, periodNorm, timeShiftVars, normCenter, var74Selector, floatDataGetter ]]
transformedData = transformData(dataDescription)

classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l2')

regRangeTuple = ( .001,1000., 60) 
regRangeTuple = ( 0.05,0.10, 50) 
print "TESTING sweep" 
optReg = sweepRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                        predictProbs=True, yPostProcFunc=None )

print "Single test prediction using KFold"
preds = kFoldPrediction( transformedData, targetVariable, classifier(optReg),predictProbs=True )
print "Single test prediction AUC:", AUC(targetVariable, preds)

FOUT_NAME = "Sept21-Submission.csv"
fout = open(FOUT_NAME,"w")
fout.write("Timestamp,TargetVariable\n")
testMask = numpy.isnan(targetVariable)
for ts, pred in zip(timestamps[testMask], preds[testMask]):
    outString = str(round(ts,5))+","+str(pred)+"\n"
    fout.write(outString)
fout.close()
print "Wrote submission file to:", FOUT_NAME

#
# Kfold Predicted AUC for submission: 0.968393788297
# Actual AUC for submission: 0.96838
#

