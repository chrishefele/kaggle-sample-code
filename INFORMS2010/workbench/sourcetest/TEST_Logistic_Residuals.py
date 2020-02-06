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

dataDescription = [ [ var74Selector, normCenter, floatDataGetter ] ]
# dataDescription = [ [  normCenter, var74Selector, floatDataGetter ] ] 
print "Transforming data"
transformedData = transformData(dataDescription)

classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')



print "Single test prediction using KFold"
preds = kFoldPrediction( transformedData, targetVariable, classifier(0.01),predictProbs=True )
print "Single test prediction AUC:", AUC(targetVariable, preds)


var74 = transformedData["Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD"]
print "Var74 Stdev:", var74.std(), "Mean:", var74.mean()
trainMask = numpy.isfinite(targetVariable)
residuals = targetVariable[trainMask] - preds[trainMask]
indepVar = var74[trainMask]
# **** add KNN HERE????


fout_resids=open("residuals.txt","w")
#fout_var74 =open("var74.txt","w")
for tv, pred, v74 in zip(targetVariable[trainMask], preds[trainMask], var74[trainMask]):
    fout_resids.write(str(tv-pred)+"\n") 
#    fout_var74.write( str(v74)+"\n")
fout_resids.close()
#fout_var74.close()  
print "Wrote residuals to residuals.txt"



#for comparison, the logistic regression AUC vs regularization was: 
#AUC: 0.954303808341 	Parameter: 0.001
#AUC: 0.961649526398 	Parameter: 0.01
#AUC: 0.961559545241 	Parameter: 0.1
#AUC: 0.961504763655 	Parameter: 1.0
#AUC: 0.961479174888 	Parameter: 10.0
#AUC: 0.961476892322 	Parameter: 100.0

"""
regRangeTuple = ( .001,1000., 6) 
print "TESTING sweep" 
sweepRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                        predictProbs=True, yPostProcFunc=None )
"""

"""
regRangeTuple = (.001, 10, 4) 
print "TESTING optimizeRegularization"
optReg =  optimizeRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                           predictProbs=True, yPostProcFunc=None  ) 
print "Optimizer returned:", optReg
"""

