import ProvidedData
from Transforms import *
from Prediction import *
from Optimize import * 
import scikits.learn.logistic
import scikits.learn.svm

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
timestamps = pd.getTimestamps()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
intDataGetter = makeGetCategoricalVars(pd.getIntData)
var74Selector = makeSelectVars("Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD")

dataDescription = [ [ normCenter, timeShiftVars, var74Selector, normCenter, floatDataGetter ] ]
# dataDescription = [ [  normCenter, var74Selector, floatDataGetter ] ] 
print "Transforming data"
transformedData = transformData(dataDescription)
print "Transformed Data type is:", type(transformedData)

classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')
preds0 = kFoldPrediction( transformedData, targetVariable,\
                             classifier(0.01), predictProbs=True )
auc0 = AUC(targetVariable, preds0)

fracTimestamps = timestamps - numpy.fix(timestamps)
for periodNum, fracTimestamp in enumerate(sorted(list(set(fracTimestamps)))):
    fracMask = (fracTimestamps != fracTimestamp) # exclude one 5min period
    # print "Original Data pts:", len(timestamps), "Leave-one-out data pts:", sum(fracMask)
    #maskedTransformedData = {}
    #for varName in transformedData:
    #    maskedTransformedData[varName] = transformedData[varName][fracMask] 
    #maskedTargetVariable = targetVariable[fracMask] 
    preds = kFoldPrediction( transformedData, targetVariable,\
                             classifier(0.01), predictProbs=True, skipMask = fracMask )
    auc1 = AUC(targetVariable, preds)
    print "PeriodNum:", periodNum, "DayFraction:", fracTimestamp, 
    print "AUC:", auc1, "deltaAUC:", auc1-auc0


#for comparison, the logistic regression AUC vs regularization was: 
#AUC: 0.954303808341 	Parameter: 0.001
#AUC: 0.961649526398 	Parameter: 0.01
#AUC: 0.961559545241 	Parameter: 0.1
#AUC: 0.961504763655 	Parameter: 1.0
#AUC: 0.961479174888 	Parameter: 10.0
#AUC: 0.961476892322 	Parameter: 100.0


