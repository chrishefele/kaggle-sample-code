import ProvidedData
from Transforms import *
from Prediction import *
import scikits.learn.logistic
import math

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
timestamps = pd.getTimestamps()
selectVar74 = makeSelectVars("Variable74_LASTLASTRETURN")

dataDescription = [ [ normCenter, percentileVars, normCenter, selectVar74, floatDataGetter ] ]
# dataDescription = [ [ normCenter, selectVar74, floatDataGetter ] ]

print "Transforming data"
transformedData = transformData(dataDescription)
# print transformedData
print "Now testing predictions"

#var74Data = transformedData["Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD"] 
var74Data = transformedData["Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD_PERCENTILE_CTRMEAN_NORMSTD"] 
fracTimestamps = timestamps - numpy.fix(timestamps) 
trainMask = numpy.isfinite(targetVariable) 
sumSquares={}
sumReturns={}
for fts, var74datum in zip(fracTimestamps[trainMask], var74Data[trainMask]):
    if fts in sumSquares and fts in sumReturns:
        sumSquares[fts] = sumSquares[fts] + var74datum*var74datum
        sumReturns[fts] = sumReturns[fts] + var74datum
    else:
        sumSquares[fts] = var74datum*var74datum
        sumReturns[fts] = var74datum
fractionalTimestamps = sumSquares.keys()
for fts in sorted(fractionalTimestamps):
    print "Time:",fts,"RootSumSquares:",math.sqrt(sumSquares[fts]/len(fractionalTimestamps)),
    print "SumReturns:",sumReturns[fts]/len(fractionalTimestamps)


     

