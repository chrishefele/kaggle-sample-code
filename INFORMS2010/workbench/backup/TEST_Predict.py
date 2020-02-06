import ProvidedData
from Transforms import *
from Prediction import *
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
# dataDescription = [ [ normCenter, doAnchoredPCAvar74, normCenter, floatDataGetter ] ] 
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


