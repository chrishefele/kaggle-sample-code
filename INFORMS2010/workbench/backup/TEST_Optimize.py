import ProvidedData
from Transforms import *
from Prediction import *
from Optimize import * 
import scikits.learn.logistic

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
intDataGetter = makeGetCategoricalVars(pd.getIntData)
doAnchoredPCAvar74 = makeDoAnchoredPCA("Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD") 

dataDescription = [ [normStd, centerMean, floatDataGetter], \
                    [normStd, centerMean, doPCA, normStd, centerMean, floatDataGetter], \
                    [gradientVars, integrateVars, normStd, centerMean, floatDataGetter],\
                    [diffVars , integrateVars, normStd, centerMean, floatDataGetter]  ]  

dataDescription = [ [ timeShiftVars, normCenter, floatDataGetter ] ]
dataDescription = [ [ normCenter, doPCA, normCenter, floatDataGetter ] ] 
dataDescription = [ [ normCenter, floatDataGetter ] ]

print "Transforming data"
transformedData = transformData(dataDescription)
# print transformedData
print "Now testing predictions"

print "Predicting...using KFold"
classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')
preds = kFoldPrediction( transformedData, targetVariable, classifier(0.01) )
print "Finished predicting"
print "AUC:", AUC(targetVariable, preds)


regRangeTuple = (.001, 1, 4) 
classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l2')
predVars = transformedData
targetVar = targetVariable
print "TESTING sweepRegularization" 
sweepRegularization(regRangeTuple, classifier, predVars, targetVar, \
                        predictProbs=True, yPostProcFunc=None )

regRangeTuple = (.001, 1, 4) 
classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l2')
predVars = transformedData
targetVar = targetVariable
print "TESTING optimizeRegularization"
optReg =  optimizeRegularization(regRangeTuple, classifier, predVars, targetVar, \
                           predictProbs=True, yPostProcFunc=None  ) 
print "Optimizer returned:", optReg


