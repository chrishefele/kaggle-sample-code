from Prediction import * 
import math

# Note: for both optimizeRegularization and sweepRegularization, you 
# must pass a classifier function that is itself a function 
# of regularization only, with all other parameters already set, e.g.
#  classifier = lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')
# so classifer is a function of reg only, with 'penalty' already set in this example.
# Also, make sure the 'predictProbs' flag is set true/false to match the 
# kind of predictions the classifer function creates 

def optimizeRegularization(regRangeTuple, classifier, predVars, targetVar, \
                           predictProbs=True, yPostProcFunc=None  ): 
    if len(regRangeTuple) == 3:
        regLow, regHigh, _ = regRangeTuple 
    else:
        regLow, regHigh = regRangeTuple
    print "Optimizing regularization in range: [", regLow,",",regHigh,"]"
    def func(regularization):
        predictions = kFoldPrediction(predVars, targetVar, classifier(regularization),\
                                      predictProbs=predictProbs, yPostProcFunc=yPostProcFunc)
        return -AUC(targetVar, predictions) 

    displayLevel=3 # 0=no messages, 3=most verbose
    funcExtraArgs=()
    regOptimal, negAUCOptimal, errorFlag,numFuncCalls = \
        scipy.optimize.fminbound(func, regLow, regHigh, args=funcExtraArgs, \
                                 full_output=True, disp=displayLevel       )
    print "OptimalAUC:", -negAUCOptimal, "OptimalRegularization:", regOptimal
    return regOptimal

def sweepRegularization(regRangeTuple, classifier, predVars, targetVar, \
                        predictProbs=True, yPostProcFunc=None ):
    # sweep from low to high parameter values using exponential steps
    regLo, regHi, regN = regRangeTuple
    logRegLo, logRegHi = ( math.log(regLo) , math.log(regHi) ) 
    logRegStepSize = (logRegHi - logRegLo) / regN
    logReg = logRegLo
    results = []
    bestResult = (0. , 0.)
    while logReg <= logRegHi:
        reg = math.exp(logReg)
        # calc AUC with this reg
        predictions = kFoldPrediction(predVars, targetVar, classifier(reg),\
                                      predictProbs=predictProbs, yPostProcFunc=yPostProcFunc)
        auc = AUC(targetVar, predictions) 
        print "Parameter:",reg,"AUC:", auc
        results.append((reg,auc))
        bestReg, bestAUC = bestResult
        if auc >= bestAUC:
            bestResult = (reg, auc)
        logReg += logRegStepSize
    print "\nSweep Results"
    for reg, auc in results:
        print "AUC:", auc, "\tParameter:",reg
    print
    bestReg, bestAUC = bestResult
    print "Best Sweep AUC:", bestAUC," at parameter:", bestReg
    return bestReg

sweepParameter = sweepRegularization  # def's a different func name for non-reg parameters      


