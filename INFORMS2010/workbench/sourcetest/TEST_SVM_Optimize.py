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

#dataDescription = [ [ timeShiftVars, normCenter, floatDataGetter ] ]
#dataDescription = [ [ normCenter, floatDataGetter ] ]
# dataDescription = [ [ timeShiftVars, normCenter, percentileVars, var74Selector, normCenter, floatDataGetter ] ]
dataDescription = [ [ normCenter, timeShiftVars, var74Selector, normCenter, floatDataGetter ] ]
# dataDescription = [ [  normCenter, var74Selector, floatDataGetter ] ] 
print "Transforming data"
transformedData = transformData(dataDescription)

class mySVC: 
# wrapper class to invert the returned result to predict prob(1), not prob(0) 
    def __init__(self, **kwargs):
        self._SVC = scikits.learn.svm.SVC(**kwargs)
    def fit(self,X,Y):
        self._SVC.fit(X,Y)
    def predict_proba(self,X):
        return 1.0 - self._SVC.predict_proba(X)   # maps 0->1, 1->0

#classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')
#classifier = lambda reg:   mySVC(C=reg, kernel='linear', probability=True)
# radial basis function: exp(-gamma*|u-v|^2) ; gamma default = 1/num_features
classifier = lambda reg:   mySVC(C=reg, kernel='rbf', probability=True)
#classifier = lambda gamma: mySVC(C=1000.0, kernel='rbf', gamma=gamma, probability=True)

"""
print "Single test prediction using KFold"
preds = kFoldPrediction( transformedData, targetVariable, classifier(0.1),predictProbs=True )
print "Single test prediction AUC:", AUC(targetVariable, preds)
print "Inverted test prediction AUC:", AUC(targetVariable, 1.0-preds)
"""

# with linear svm-rbf, here's auc vs regularization: 
#AUC: 0.950122747993 	Parameter: 0.0001
#AUC: 0.952383269271 	Parameter: 0.001
#AUC: 0.957505828052 	Parameter: 0.01
#AUC: 0.960296445264 	Parameter: 0.1
#AUC: 0.960521878696 	Parameter: 1.0
#AUC: 0.960541821115 	Parameter: 10.0
#AUC: 0.96055167219 	Parameter: 100.0; tolerably long 
#AUC: 0.960556357457 	Parameter: 1000.0; very long
# RBF with default gamma
#AUC: 0.947199922152 	Parameter: 0.001
#AUC: 0.949199630224 	Parameter: 0.01
#AUC: 0.949756576343 	Parameter: 0.1
#AUC: 0.951177113311 	Parameter: 1.0
#AUC: 0.954852645344 	Parameter: 10.0
#AUC: 0.95977776216 	Parameter: 100.0
#AUC: 0.960613721946 	Parameter: 1000.0 # tollerably long in rbf (vs linear)
#AUC: 0.960618707551 	Parameter: 1000.0 <<<PEAK? 
#AUC: 0.95869576578 	Parameter: 10000.0
#AUC: 0.957788866243 	Parameter: 100000.0
#AUC: 0.957805805286 	Parameter: 1000000.0
# with RBF, C=reg=1000, gamma varying, we get:
#AUC: 0.95370415421 	Parameter: 1e-06
#AUC: 0.959079176811 	Parameter: 1e-05
#AUC: 0.960428834095 	Parameter: 0.0001
#AUC: 0.958005830154 	Parameter: 0.001
#AUC: 0.958069862139 	Parameter: 0.01
#AUC: 0.955019392801 	Parameter: 0.1
#AUC: 0.942581810471 	Parameter: 1.0
#AUC: 0.868129731444 	Parameter: 10.0

#for comparison, the logistic regression AUC vs regularization was: 
#AUC: 0.954303808341 	Parameter: 0.001
#AUC: 0.961649526398 	Parameter: 0.01
#AUC: 0.961559545241 	Parameter: 0.1
#AUC: 0.961504763655 	Parameter: 1.0
#AUC: 0.961479174888 	Parameter: 10.0
#AUC: 0.961476892322 	Parameter: 100.0


regRangeTuple = ( 100.,100000., 3) 
print "TESTING sweep" 
sweepRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                        predictProbs=True, yPostProcFunc=None )
#sweepParameter(regRangeTuple, classifier, transformedData, targetVariable, \
#                       predictProbs=True, yPostProcFunc=None )


"""
regRangeTuple = (.001, 10, 4) 
print "TESTING optimizeRegularization"
optReg =  optimizeRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                           predictProbs=True, yPostProcFunc=None  ) 
print "Optimizer returned:", optReg
"""

