import ProvidedData
from Transforms import *
from Prediction import *
from Optimize import * 
import scikits.learn.logistic
import scikits.learn.svm

def goDoIt(allowMultidayReturns, returnPeriod, eodPeriod):
    pd = ProvidedData.ProvidedData(allowMultidayReturns=allowMultidayReturns, \
                            returnPeriod = returnPeriod, eodPeriod = eodPeriod)
    targetVariable = pd.getTargetVar()
    floatDataGetter = makeGetFloatVars(pd.getFloatData)
    intDataGetter = makeGetCategoricalVars(pd.getIntData)
    var74Selector = makeSelectVars("Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD")

    dataDescription = [ [ var74Selector, normCenter, floatDataGetter ] ]
    transformedData = transformData(dataDescription)
    classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')
    regRangeTuple = ( .001,1000., 6) 
    sweepRegularization(regRangeTuple, classifier, transformedData, targetVariable, \
                            predictProbs=True, yPostProcFunc=None )

for allowMultidayReturns in [True, False]:
    for returnPeriod in [11,12,13]:
        for eodPeriod in [-1,-2]:
            print "\n*** MultidayReturns:", allowMultidayReturns,
            print " ReturnPeriod:", returnPeriod,
            print " EndOfDayPeriod:", eodPeriod
            goDoIt(allowMultidayReturns, returnPeriod, eodPeriod)

