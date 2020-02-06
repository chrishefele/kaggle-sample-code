import ProvidedData
from Transforms import *
from Prediction import *
from Optimize import * 
import scikits.learn.logistic
import scikits.learn.svm

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
intDataGetter = makeGetCategoricalVars(pd.getIntData)
var74Selector = makeSelectVars("Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD")

dataDescription = [ [ normCenter, timeShiftVars, var74Selector, normCenter, floatDataGetter ] ]
# dataDescription = [ [  normCenter, var74Selector, floatDataGetter ] ] 
print "Transforming data"
transformedData = transformData(dataDescription)

classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')

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
regRangeTuple = (.001, 10, 4) 
print "TESTING optimizeRegularization"
optReg =  optimizeRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                           predictProbs=True, yPostProcFunc=None  ) 
print "Optimizer returned:", optReg
"""

