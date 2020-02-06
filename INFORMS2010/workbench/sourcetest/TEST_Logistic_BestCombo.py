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


dataDescription = [ [getTimeOfDayMeanTargetVar], [ percentileVars, periodNorm, timeShiftVars, normCenter, var74Selector, floatDataGetter ] ]
transformedData = transformData(dataDescription)

classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l2')


"""
print "Single test prediction using KFold"
preds = kFoldPrediction( transformedData, targetVariable, classifier(0.01),predictProbs=True )
print "Single test prediction AUC:", AUC(targetVariable, preds)
print "Inverted test prediction AUC:", AUC(targetVariable, 1.0-preds)
"""

#for comparison, the logistic regression AUC vs regularization was: 
#AUC: 0.954303808341 	Parameter: 0.001
#AUC: 0.961649526398 	Parameter: 0.01
#AUC: 0.961559545241 	Parameter: 0.1
#AUC: 0.961504763655 	Parameter: 1.0
#AUC: 0.961479174888 	Parameter: 10.0
#AUC: 0.961476892322 	Parameter: 100.0

regRangeTuple = ( .001,1000., 6) 
print "TESTING sweep" 
sweepRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                        predictProbs=True, yPostProcFunc=None )

"""
preprocessors = [dayCenter, periodCenter, dayNorm, periodNorm, passthruVars, passthruVars]

for ix1,ix2,ix3,ix4 in itertools.permutations([0,1,2,3,4,5],4):
    f1 = preprocessors[ix1]
    f2 = preprocessors[ix2]
    f3 = preprocessors[ix3]
    f4 = preprocessors[ix4]
    dataDescription = [ [ f1,f2,f3,f4, var74Selector, floatDataGetter ] ]
    transformedData = transformData(dataDescription)
    regRangeTuple = (.001, 1000.0, 6) 
    #optReg =  optimizeRegularization(regRangeTuple, classifier, \
    #                            transformedData, targetVariable, \
    #                            predictProbs=True, yPostProcFunc=None  ) 
    optReg = 100.0
    preds = kFoldPrediction(    transformedData, targetVariable, \
                                classifier(optReg),predictProbs=True )
    auc = AUC(targetVariable, preds) 
    # dataDescr = printDataDescription(dataDescription, silent=True)
    print "RESULT: OptimalAUC:", auc, "OptReg:", optReg,
    print "Data:",[ix1,ix2,ix3,ix4]

"""




