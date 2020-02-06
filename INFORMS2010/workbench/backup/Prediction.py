import scipy.optimize
from scikits.learn.metrics import roc, auc
from scikits.learn.cross_val import KFold
import scikits
import numpy
import sys

def _makeXDataArrayFromDict(xDataDict):
    varNames = xDataDict.keys()
    return numpy.column_stack( [xDataDict[varName] for varName in sorted(varNames)] )
        
def _extractPredictions(x):
    if len(x.shape) == 1:  # for Ridge regression, returns only 1 column 
        return x
    else:
        CLASS_1_COL = 0     #col with class 1 predictions in Logistic Regression, at least! 
        return x[:,CLASS_1_COL]

def kFoldPrediction(xDataDict, yDataArray, classifier, \
                    predictProbs=True, yPostProcFunc=None, KFOLDS=9, skipMask=None):
    xDataArray = _makeXDataArrayFromDict(xDataDict)
    allTrainDataMask = numpy.isfinite(yDataArray) #relies on NaNs put in test positions
    allTestDataMask  = numpy.isnan(yDataArray)
    testX,  testY  = (xDataArray[allTestDataMask], yDataArray[allTestDataMask] )
    trainX, trainY = (xDataArray[allTrainDataMask],yDataArray[allTrainDataMask])
    # skipMask[]=False where need to skip data during training (e.g. for outliers)
    if skipMask != None: 
        trainSkipMask = skipMask[allTrainDataMask]
    else:
        skipMask = numpy.array([True]*len(allTrainDataMask)) #don't skip anything
        trainSkipMask = skipMask[allTrainDataMask]
    # make predictions for training data using K-Folds
    allTrainFoldPredictions = numpy.array([])
    currentFold = 0 
    print "Training KFold",
    for foldTrainMask, foldTestMask in KFold( len(trainY), KFOLDS ):
        currentFold += 1
        print currentFold, 
        sys.stdout.flush()
        classifier.fit( trainX[foldTrainMask & trainSkipMask],\
                        trainY[foldTrainMask & trainSkipMask]) # added trainSkipMask
        if predictProbs and ('predict_proba' in dir(classifier)):  # calc probs only if you can
            foldPredictions = classifier.predict_proba(trainX[foldTestMask])
        else:
            foldPredictions = classifier.predict(trainX[foldTestMask]) 
        foldPredictions = _extractPredictions(foldPredictions) 
        allTrainFoldPredictions = numpy.concatenate((allTrainFoldPredictions, foldPredictions))
    # now make predictions for test data using model created from all training data
    print "Test",
    sys.stdout.flush()
    classifier.fit(trainX, trainY)
    if predictProbs and ('predict_proba' in dir(classifier)): # calc probs only if you can
        testPredictions = classifier.predict_proba(testX)
    else:
        testPredictions = classifier.predict(testX)
    testPredictions = _extractPredictions(testPredictions)
    allPredictions = numpy.concatenate((allTrainFoldPredictions, testPredictions))
    if yPostProcFunc!=None:
        allPredictions = yPostProcFunc(allPredictions)
    print 
    return allPredictions # kfold training set predictions & test set predictions

    
def AUC(targetVariable, allPredictions):
    AUC_DEC_PTS = 3  # decimal points to round predictions to, to speed AUC calculation
    trainMask = numpy.isfinite(targetVariable)
    targetVariableTrainOnly = targetVariable[trainMask]
    predictionsTrainOnly = allPredictions[trainMask]
    predictionsTrainOnly = numpy.round(predictionsTrainOnly, decimals=AUC_DEC_PTS) #new
    FPR, TPR, thresholds = roc(targetVariableTrainOnly, predictionsTrainOnly) 
    roc_auc = auc(FPR, TPR)
    return roc_auc


