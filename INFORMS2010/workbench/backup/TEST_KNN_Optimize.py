import ProvidedData
from Transforms import *
from Prediction import *
from Optimize import * 
import scikits.learn.logistic
import scikits.learn.svm
import scikits.learn.neighbors

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
intDataGetter = makeGetCategoricalVars(pd.getIntData)
var74Selector = makeSelectVars("Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD")

#dataDescription = [ [ timeShiftVars, normCenter, floatDataGetter ] ]
#dataDescription = [ [ normCenter, floatDataGetter ] ]
# dataDescription = [ [ timeShiftVars, normCenter, percentileVars, var74Selector, normCenter, floatDataGetter ] ]
dataDescription = [ [ normCenter, timeShiftVars, var74Selector, normCenter, floatDataGetter ] ]
dataDescription = [ [ normCenter, var74Selector, normCenter, floatDataGetter ] ]

print "Transforming data"
transformedData = transformData(dataDescription)

# classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')
# classifier = lambda reg: scikits.learn.svm.SVC(C=reg, kernel='linear')

classifier = lambda K:   scikits.learn.neighbors.Neighbors(k=K)

print "Single test prediction using KFold"
preds = kFoldPrediction( transformedData, targetVariable, classifier(4),predictProbs=False )
print "Single test prediction AUC:", AUC(targetVariable, preds)

'''
# note: optimum is around 4 to 16; broad non-smooth boundry
for log2k in range(1,10):
    k=pow(2,log2k)
    preds = kFoldPrediction( transformedData, targetVariable, classifier(k),predictProbs=False )
    print "Neighbors:",k, "AUC:", AUC(targetVariable, preds)
''' 


"""
regRangeTuple = (.001, 1000, 6) 
print "TESTING sweep" 
#sweepRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
#                        predictProbs=False, yPostProcFunc=None )
sweepParameter(regRangeTuple, classifier, transformedData, targetVariable, \
                        predictProbs=False, yPostProcFunc=None )
"""


"""
regRangeTuple = (.001, 10, 4) 
print "TESTING optimizeRegularization"
optReg =  optimizeRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                           predictProbs=False, yPostProcFunc=None  ) 
print "Optimizer returned:", optReg
"""

