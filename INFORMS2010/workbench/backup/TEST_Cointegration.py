import ProvidedData
from Transforms import *
from Prediction import *
from Optimize import * 
import scikits.learn.logistic
import scikits.learn.glm
import itertools

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
intDataGetter = makeGetCategoricalVars(pd.getIntData)
var74Selector = makeSelectVars("Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD")

# ********************
dataDescription = [ [ normCenter, integrateVars,  var74Selector, normCenter, floatDataGetter ] ]
# AUC: 0.954309274486 Reg: 1 Ridge/L2
# Note: adding timeshift was WORSE! 0.9445 (perhaps due to L2?) 
# ********************

def go(dataDescription):
    transformedData = transformData(dataDescription)

    classifier = lambda reg: scikits.learn.glm.Ridge(alpha=reg)
    #classifier = lambda reg: scikits.learn.glm.Lasso(alpha=reg) #CHANGE BACK TO RIDGE
    # diffFunc = lambda x: numpy.ediff1d(x, to_begin=0) # NOTE: Gradient works better
    diffFunc = lambda x: numpy.gradient(x)

    trainMask = numpy.isfinite(targetVariable)
    testMask  = numpy.isnan(targetVariable)
    tv1= numpy.cumsum( targetVariable[trainMask]-targetVariable[trainMask].mean() )
    intTargetVariable = numpy.copy(targetVariable)
    intTargetVariable[trainMask] = (tv1-tv1.mean()) 

    print "Predicting...using KFold"
    for log10reg in range(-5,9):
        reg = pow(10,log10reg)
        intPreds = kFoldPrediction( transformedData, intTargetVariable, \
                                    classifier(reg), predictProbs=False )
        preds = diffFunc(intPreds)
        print "AUC:", AUC(targetVariable, preds), "Reg:", reg
    return preds # just to have a look a the scaled data...

predictions = go(dataDescription)

# just to have a look at the scaled data...
predictionsDict = {"Predictions":predictions}
percentilePredictionsDict = percentileVars(predictionsDict)
percentilePredictions = percentilePredictionsDict["Predictions_PERCENTILE"]





