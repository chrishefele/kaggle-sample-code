import ProvidedData
from Transforms import *
from Prediction import *
from Optimize import * 
import numpy
import scikits.learn.logistic
import scikits.learn.svm
import Cointegration

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
intDataGetter = makeGetCategoricalVars(pd.getIntData)
var74Selector = makeSelectVars("Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD")

dataDescription = [ [ var74Selector, normCenter, floatDataGetter ] ]
# dataDescription = [ [ normCenter, floatDataGetter ] ]
transformedData = transformData(dataDescription)

classifier = lambda reg: Cointegration.Cointegration(C=reg, penalty='l2') 

print "Single test prediction using KFold"
preds = kFoldPrediction( transformedData, targetVariable, classifier(0.01),predictProbs=False )
print "Single test prediction AUC:", AUC(targetVariable, preds)

regRangeTuple = ( .001,1000., 6) 
print "TESTING sweep" 
sweepRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                        predictProbs=False, yPostProcFunc=None )

"""
regRangeTuple = (.001, 10, 4) 
print "TESTING optimizeRegularization"
optReg =  optimizeRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                           predictProbs=False, yPostProcFunc=None  ) 
print "Optimizer returned:", optReg
"""

