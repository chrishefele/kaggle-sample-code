#!/usr/bin/python

# =============================================================================
# INFORMS Data Mining Contest 2010 program
# Chris Hefele July, 2010
#
# =============================================================================

from numpy import array
import numpy, numpy.random
import math
import sys
import time
import scipy.signal, scipy.optimize
from scikits.learn.logistic import LogisticRegression
from scipy import interp
from scikits.learn.metrics import roc, auc
from scikits.learn.cross_val import KFold

# =============================================================================
TESTING_FILE  = "/home/chefele/INFORMS2010/data/ResultData.csv"
TRAINING_FILE = "/home/chefele/INFORMS2010/data/TrainingData.csv"

# Define variable types used in the files above
VARS_POSSIBLE_INTS = set(range(143,155+1)+range(161,163+1)+[142])
VARS_POSSIBLE_FLOATS = set( [156]+[157,159,160,164,165]+ \
                            range(167,180+1)+range(8,141+1))

VARS_MISSING_INTS = set([156]) # result range > training range, so make it a float
VARS_MISSING_FLOATS = set([ 16,39,66,67,75,84,96,104,106,110,118,\
                            119,122,128,131,132,134,135,138,140])

VARS_INTS   = VARS_POSSIBLE_INTS    - VARS_MISSING_INTS     
VARS_FLOATS = VARS_POSSIBLE_FLOATS  - VARS_MISSING_FLOATS 

RETURN_PERIOD = 12 # calc stock returns over this many 5min periods (12*5min=1hr)

FOLDS = 9 # for kfolds cross validation

# =============================================================================

def readDataFile(filename):
    print "Reading:", filename
    sys.stdout.flush()
    fin = open(filename,"r")   
    titlesLine = fin.readline()
    inTitles = [inTitle.strip() for inTitle in titlesLine.split(",")] 
    inData={}
    for inTitle in inTitles:
        inData[inTitle]=[]
    for dataLine in fin.readlines():
        inDatums = [datum.strip() for datum in dataLine.split(",")] 
        for inTitle, inDatum in zip(inTitles, inDatums):
             inData[inTitle].append(inDatum)
    print "Finished reading:", filename
    return inData

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def floatWithDefault(valString, valIfNotNumber):
    if isNumber(valString):
        return float(valString)
    else:
        return float(valIfNotNumber)

def replaceZero(x,zeroReplacement):
    if x==0.0:
        return zeroReplacement
    else:
        return x 

def numUniqVals(strList):
    return len( set(strList) - set(["","-"]) ) 

def meanNonMissingFloatVals(strList):
    floatVals = array( [float(s) for s in strList if isNumber(s)] )
    return floatVals.mean()

def booleanToBinary(b):
    if b:
        return 1
    else:
        return 0 

def timeShift(vals, shift): 
    if shift > 0:  # move future values into the past
        shiftedVals = vals[shift:]  # drop FIRST shift vals 
        padding = numpy.empty(abs(shift)) 
        padding.fill(shiftedVals[-1]) # pad RIGHT with LAST value 
        return numpy.concatenate((shiftedVals,padding)) 
    elif shift < 0: # move past values into the future 
        shiftedVals = vals[:shift] # drop LAST shift vals (shift is negative)
        padding = numpy.empty(abs(shift))
        padding.fill(shiftedVals[0]) # pad LEFT with FIRST value
        return numpy.concatenate((padding, shiftedVals))
    else:
        return vals 
        
def makeFloatVars(inData, returnPeriods):
    outData = {}
    # for floating-point variables (e.g. mostly stock prices)
    for varFloat in VARS_FLOATS:
        # search for the first variable name with data present (in preferential order)
        varPrefix = "Variable"+str(varFloat)
        for varSuffix in ["LAST_PRICE", "LAST", "OPEN"]: 
            varName = varPrefix + varSuffix 
            if varName in inData:
                break
        else:
            raise UserWarning("Cannot find variable with prefix "+varPrefix)
        inVals = inData[varName]
        avg = meanNonMissingFloatVals(inVals)
        newVals = [ floatWithDefault(s,avg) for s in inVals ] # replace missing data with avg
        newVals = [ replaceZero(x, avg) for x in newVals ] # replace 0's with avg (for var22) 
        newVals = numpy.array(newVals)
        # instead of price, use log-normalized price change over 'returnPeriods'
        timeShiftedNewVals = timeShift(newVals,returnPeriods) # get future prices
        newVals = numpy.log10(timeShiftedNewVals) - numpy.log10(newVals)
        outData[varName] = newVals #normalized later!!
        # add a binary version of the returns based on sign (+=1,-=0)
        sgns = numpy.sign(newVals)
        if abs(max(sgns)-min(sgns)) > 1E-10 : # signs all different (1,-1)
            outData[varName+"_SIGN"] = (numpy.sign(newVals)+1.0)/2.0
        else:
            # don't add sign variable if all signs the same; avoids collinearity w intercept
            print "Warning: "+varName+"_SIGN"+" not added; all signs identical"
    return outData
            
def makeCubicVars(inData, varNames):
    outData = {}
    for varName in varNames:
        varValues = inData[varName]
        normValues = (varValues - varValues.mean()) / varValues.std()
        outData[varName+"_SQUARED"] = pow(normValues,2)
        outData[varName+"_CUBED"]   = pow(normValues,3)
    return outData
    
def makeCrossProductVars(inData, varNames):
    outData = {}
    for varName in varNames:
        varValues      = inData[varName]
        varValuesLag1  = timeShift(varValues, 1)
        varValuesLead1 = timeShift(varValues,-1)
        outData[varName + "_T+0*T+1"]     = varValues * varValuesLag1
        outData[varName + "_T+0*T-1"]     = varValues * varValuesLead1
        outData[varName + "_T+1*T-1"]     = varValuesLag1 * varValuesLead1
        outData[varName + "_T+1*T+0*T-1"] = varValuesLag1 * varValues * varValuesLead1
    return outData

def makePercentileVars(inData, varNames):
    outData = {}
    for varName in varNames:
        varValues = inData[varName]
        l = [ (varVal,index0) for index0, varVal in enumerate(varValues) ]
        l.sort() # sort by values
        l = [ (index0, varVal, index1) for index1, (varVal, index0) in enumerate(l) ]
        l.sort() # sort by original index
        numVals = float(len(l))
        percentileVals = array([ index1/numVals for index0, varVal, index1 in l ])
        outData[varName+"_PERCENTILE"] = percentileVals
    return outData

def makeMultipleTimeshifts(inData, varNames):
    outData = {}
    MAX_SHIFT = 12 
    for varName in varNames:
        for shift in range(-MAX_SHIFT,-1+1) + range(1,MAX_SHIFT+1):
            suffix = "_SHIFT_"+str(shift)
            outData[varName + suffix] = timeShift( inData[varName], shift )
    return outData


def makeIntVars(inData):
    outData = {}
    # for integer/categorical variables (e.g. not stock prices)
    for varInt in VARS_INTS:
        varName = "Variable"+str(varInt)+"LAST"
        inVals = inData[varName]
        # now add new 0|1 column for each non-missing value/category
        colVals = set(inVals) - set([""])  # don't need a missing ("") value category
        for colVal in colVals: 
            newVals = [ booleanToBinary(colVal==thisVal) for thisVal in inVals ]
            newVals = numpy.array(newVals)
            newVarName = varName + "=" + colVal
            outData[newVarName] = newVals
    return outData

def makeTargetVar(inData):
    outData = {}
    varName = "TargetVariable"
    if varName in inData:  # i.e. if Training; TagetVariable is not in "Results.csv"
        outData[varName] = numpy.array( [float(x) for x in inData[varName]] ) 
    return outData

def makeRandomVars(inData):
    outData = {}
    numRands = len(inData["Timestamp"])
    outData["RandomNormal"] = numpy.random.randn(numRands) 
    outData["RandomBinary"] = numpy.random.random_integers(0,1,numRands)
    return outData 

def timestampToPeriod(ts):
    #converts from a timestamp string to the integer 0-78 of the 5 minute period
    #in the trading day;  9:30 is 0, and 4pm is 78
    t = float(ts)
    dayFraction = t - int(t) 
    dayPeriod = dayFraction*12*24 - 114
    return int(round(dayPeriod,0))

def makeTimeVars(inData):
    outData = {}
    # add timestamp 
    varName = "Timestamp"
    outData[varName] = numpy.array( [float(x) for x in inData[varName]] ) 
    #
    # make time of day a categorical variable by using the timestamp to get 
    # the 5min period bins of the trading day (0<=bin#<=78) and then add a new
    # binary 0|1 categorical variable for each 5min bin (except the earliest)
    timestamps = inData["Timestamp"] 
    fiveMinPeriods = [timestampToPeriod(ts) for ts in timestamps] 
    colVals = list( set(fiveMinPeriods) - set([min(set(fiveMinPeriods))]) )
    colVals.sort()
    for colVal in colVals: 
        newVals = [ booleanToBinary(colVal==thisVal) for thisVal in fiveMinPeriods ]
        newVals = numpy.array(newVals)
        newVarName = "Time5MinBin=" + str(colVal) 
        outData[newVarName] = newVals
    return outData

def preprocessData(inData, floatVarsReturnPeriod):
    outData = {}
    print "Transforming input data"
    floatVars = makeFloatVars(inData, floatVarsReturnPeriod)
    importantVars = ["Variable74LAST_PRICE"] 
    makeTransforms = [\
        floatVars,\
        makePercentileVars(floatVars, importantVars),\
        makeCubicVars(floatVars, importantVars),\
        makeMultipleTimeshifts(floatVars, importantVars),\
        makeCrossProductVars(floatVars, importantVars),\
        makeIntVars(inData),\
        makeTimeVars(inData),\
        makeTargetVar(inData)\
        ] 
    for makeTransform in makeTransforms:
        outData = dict( outData.items() + makeTransform.items() )
    print "Finished transforming input data"
    return outData 
    """
    outData = dict( outDataFloats.items() + outDataInts.items() + \
                    outDataTime.items() + outDataTarget.items() + \
                    outDataRandoms.items() + outDataPercentile.items() + outDataCubic.items() )
    """
         

def printVarStats(d):
    print "\nVariable Statistics\n"
    keys = d.keys()
    keys.sort()
    for key in keys:
        print key,  
        print "\tRange: [",d[key].min(),",",d[key].max(),"]", 
        print "\tAvg:  %8.5f" % d[key].mean(), 
        print "\tNumVals:", len(d[key]),
        uniqs = len(set(d[key]))
        print "\tNumUniqVals:",uniqs
        # print "\tType:", type(d[key])

def crossCorrelationAnalysis(inData):
    # Note: run this when price CHANGES are in place, not just prices 
    MAXSHIFT = 20 
    targetName = "TargetVariable"
    targetData = inData[targetName]
    cor = scipy.signal.correlate(targetData, targetData[MAXSHIFT: -MAXSHIFT], mode='valid')
    cor = cor / float(max(abs(cor)))
    print "Target Autocorrelation"
    print cor
    #
    sumCor = None 
    keys = inData.keys()
    keys.sort()
    for varName in keys:
        if varName != targetName:
            varData = inData[varName] 
            cor = scipy.signal.correlate(targetData, varData[MAXSHIFT: -MAXSHIFT], mode='valid')
            cor = cor / float(max(abs(cor)))
            if sumCor != None: 
                sumCor += cor
            else:
                sumCor = cor
            #print varName
            #print cor
            #print 
    print "\nVariable Cross-Correlation Sum"
    print sumCor/max(sumCor)

def writeDataFile(outData, fileOutName):
    print "Writing to:",fileOutName
    keys = outData.keys()
    keys.remove("Timestamp")
    keys.sort()
    keys = ["Timestamp"] + keys
    fout = open(fileOutName,"w")
    for varName in keys:
        fout.write(varName) 
        for val in outData[varName]:
            fout.write(","+str(val))
        fout.write("\n")
    fout.close()
    print "Finished writing to :",fileOutName

def getXYVarNames(inData):
    skipNames = ["TargetVariable", "Timestamp"]
    varNames = list(set(inData.keys()) - set(skipNames))
    varNames.sort()
    return varNames

def getXData(inData):
    varNames = getXYVarNames(inData)
    xData = numpy.column_stack( [inData[varName] for varName in varNames] ) 
    return xData

def getXYData(inData):
    varNames = getXYVarNames(inData)
    xData = getXData(inData)  
    yData = inData["TargetVariable"]
    return (xData, yData)

def makeLogisticRegression(inData, regularization, penalty):
    print "Logistic regression parameters"
    print "Regularization  = ", regularization
    print "Penalty (L1/L2) = ", penalty
    print "Starting logistic regression calculation"
    sys.stdout.flush()
    xData, yData = getXYData(inData)
    logRegClassifier = LogisticRegression(C=regularization, penalty=penalty)
    logRegClassifier.fit(xData,yData)
    print "Finished logistic regression calculation"
    return logRegClassifier

def printLRCoefficients(logRegClassifier, inData):
    print "\nLogistic Regression Coefficients"
    coefficients = list( logRegClassifier.coef_[:] )[0]
    varNames = getXYVarNames(inData)
    byName = zip(varNames, coefficients)
    byName.sort()
    print "\nSorted by Name"
    print  "=============="
    for name, coef in byName:
        print "%30s   %+5.5f" % (name, coef)
    byCoef = zip(coefficients, varNames)
    byCoef.sort()
    print "\nSorted by Weight"
    print "================"
    for coef, name in byCoef:
        print "%30s   %+5.5f" % (name, coef)
    print "\n"

def RMSE(a,b):
    sqerr = (a-b)*(a-b)
    return math.sqrt(sqerr.mean())

def errorByTimeOfDay(timeStamps, yVars, xVars):
    ts = array( [ float(t) for t in timeStamps] )
    dayFractions = ts - numpy.trunc(ts) 
    ySum = {}
    xSum = {}
    count = {}
    for dayFraction, y, x in zip(dayFractions, yVars, xVars):
        ySum[ dayFraction] = ySum.get(dayFraction,0)  + y
        xSum[ dayFraction] = xSum.get(dayFraction,0)  + x
        count[dayFraction] = count.get(dayFraction,0) + 1 
    dayFractionList = list(set(dayFractions))
    dayFractionList.sort()
    print "Average ERROR vs Time of Day"
    for dayFraction in dayFractionList:
        avgErr = (ySum[dayFraction] - xSum[dayFraction]) / float(count[dayFraction])
        print "dayFraction:", dayFraction, "avgErr:", avgErr


def localTimeString():
    tm  = time.localtime()
    hr  = "%02d" % tm.tm_hour
    mn  = "%02d" % tm.tm_min
    sec = "%02d" % tm.tm_sec
    tm_str = hr+":"+mn+":"+sec
    return tm_str

def AUCkFoldLogisticRegression(regularization, inData, penalty, kFolds):
    print "\n\tCalculating AUC for regularization",regularization,"using",kFolds,"folds"
    sys.stdout.flush()
    xData, yData = getXYData(inData) 
    nSamples, nFeatures = xData.shape
    if nSamples % kFolds != 0:
        raise UserWarning("Uneven fold sizes! Must evenly divide 5922 (e.g. 2,3,7 or 9 folds")
        # 2, 3, 7, and 9 are factors of 5922 (#data points) & yield equal fold sizes
    crossValFolds = KFold(nSamples, kFolds)
    yTestDataAllFolds = array([])
    probasTestDataAllFolds = array([])
    sumAUC = 0.0
    for foldNum, (train, test) in enumerate(crossValFolds):
        # fit a new LR model for each fold's data & evaluate using AUC
        LRclassifier = LogisticRegression(C=regularization, penalty=penalty)
        probas_ = LRclassifier.fit(xData[train], yData[train]).predict_proba(xData[test])
        numNon0Coefs = sum([1 for coef in LRclassifier.coef_[:][0] if coef !=0 ])
        # probas_ contains 2 columns of probabilities, one for each of the 2 classes (0,1)
        # In the documentation, seems like col 1 is for class 1, 
        # but tests show it seems like col 0 is for class 1, so we use that below. 
        CLASS_1_COL = 0 
        # Compute ROC curve and area under the curve 
        FPR, TPR, thresholds = roc(yData[test], probas_[:,CLASS_1_COL]) 
        roc_auc = auc(FPR, TPR)
        print "\tFold:", foldNum," AUC:",roc_auc,"Non0Coefs:", numNon0Coefs,
        print "Reg:",regularization,
        print localTimeString()
        sys.stdout.flush() 
        sumAUC += roc_auc
        yTestDataAllFolds = numpy.concatenate( (yTestDataAllFolds, yData[test]) )
        probasTestDataAllFolds = \
                numpy.concatenate((probasTestDataAllFolds,probas_[:,CLASS_1_COL]) )
    FPRallFolds, TPRallFolds, thresholds = roc(yTestDataAllFolds, probasTestDataAllFolds) 
    roc_auc_allFolds = auc(FPRallFolds, TPRallFolds)
    print "AUC_all_folds:", roc_auc_allFolds,
    print "Reg:", regularization, "Penalty:",penalty, "kFolds:",kFolds,
    print localTimeString()
    return roc_auc_allFolds

def negAUCkFoldLogisticRegression(regularization, inData, penalty, kFolds):
    # need negative (vs positive) function to use a scipy fminbound routine
    return -AUCkFoldLogisticRegression(regularization, inData, penalty, kFolds)

def bulkTimeShift(inData, bulkShiftPeriods): # not needed anymore; creates no improvement
    # timeshift all independent data, except timestamp and target variable
    outData = {}
    noShiftKeys = ["Timestamp", "TargetVariable"]
    for key in inData.keys():
        if not(key in noShiftKeys):
            outData[key] = timeShift(inData[key], bulkShiftPeriods)
        else:
            outData[key] = inData[key]
    return outData

def writePredictions(predictions, testingData, outFileName):
    fout = open(outFileName, "w")
    fout.write("Timestamp,TargetVariable \n")
    timestamps = testingData["Timestamp"]
    for ts, pred in zip(timestamps, predictions):
        outputLine = str(round(float(ts),5)) + "," + str(pred)
        fout.write(outputLine + "\n")
    fout.close()
    print "Wrote predictions to:", outFileName

def alignVariables(trainingData, testingData):
    # Delete any variables that training has that test doesn't, or vice-versa
    # (except that training data keeps "TargetVariable")
    # Categorical variables that were the problem were: 
    # 'Variable142LAST=-', 'Variable155LAST=4', 'Variable153LAST=8', 
    # 'Variable150LAST=1', 'Variable153LAST=3
    print "Aligning Variables in training & testing data"
    tv = ["TargetVariable"]
    inTrainNotTest = set(trainingData.keys()) - set(testingData.keys()) - set(tv)
    inTestNotTrain = set(testingData.keys())  - set(trainingData.keys())
    for varName in inTrainNotTest:
        del trainingData[varName]
    for varName in inTestNotTrain:
        del testingData[ varName]
    inTrainNotTest = set(trainingData.keys()) - set(testingData.keys())
    inTestNotTrain = set(testingData.keys())  - set(trainingData.keys())
    print "Variables only in Training data:", inTrainNotTest
    print "Variables only in Testing  data:", inTestNotTrain   
    print "Finished aligning variables"

def normalizeData(trainingData, testingData):
    # normalize values on training+testing data, not just each seperately
    print "Renormalizing data"
    renormedData = {}
    tstamp = set(["Timestamp"])
    varNames = set(trainingData.keys()).intersection(set(testingData.keys())) - tstamp
    varNames = [varName for varName in varNames if not "Timestamp" in varName] # ???debug
    for varName in varNames:
        allVals = numpy.concatenate((trainingData[varName], testingData[varName]))
        if len(set(allVals)) > 3:  #if not a binary/categorical variable...
            # then normalize the values (inplace)
            trainingData[varName] = (trainingData[varName] - allVals.mean()) / allVals.std()
            testingData[ varName] = (testingData[ varName] - allVals.mean()) / allVals.std()
            renormedData[varName] = (allVals - allVals.mean()) / allVals.std()
    print "Done renormalizing data" 
    return renormedData

def optimizeRegularization(regLow, regHigh, penalty, trainingData): 
    print "Optimizing regularization..."
    func = negAUCkFoldLogisticRegression #returns -AUC, since looking for minimum
    args = (trainingData, penalty, FOLDS)
    displayLevel=3 # 0=no messages, 3=most verbose
    regOptimal, negAUCOptimal, errorFlag,numFuncCalls = \
                    scipy.optimize.fminbound(func, regLow, regHigh, args=args, \
                                          full_output=True, disp=displayLevel)
    print "\nOPTIMIZATION RESULTS"
    print "Optimal regularization:", regOptimal,
    print "  Optimal AUC:", -negAUCOptimal
    print "L1 or L2 penalty used :", penalty
    print "Num of kFold AUC calls:", numFuncCalls
    print "\nDone optimizing regularization.\n"
    return regOptimal

def sweepRegularization(regSweep, penalty, trainingData):
    regLo, regHi, regN = regSweep
    logRegLo, logRegHi = ( math.log(regLo) , math.log(regHi) ) 
    logRegStepSize = (logRegHi - logRegLo) / regN
    logReg = logRegLo
    results = []
    while logReg <= logRegHi:
        reg = math.exp(logReg)
        # calc AUC with this reg
        auc = AUCkFoldLogisticRegression(reg, trainingData, penalty, FOLDS)
        results.append((reg,auc))
        logReg += logRegStepSize
    print "\nRegularization Sweep Results"
    for reg, auc in results:
        print "AUC:", auc, "\tReg:",reg
    print
      
          
def doCalculations(flagPrintVarStats,flagPrintLRCoef, \
                    outFileName, saveVarsFilename, regRange, regSweep, penalty):

    print "\n*** INFORMS 2010 Data Mining Contest Program ***\n"
    rawTrainingData = readDataFile(TRAINING_FILE)
    rawTestingData  = readDataFile(TESTING_FILE)
    trainingData = preprocessData(rawTrainingData, RETURN_PERIOD)
    testingData  = preprocessData(rawTestingData , RETURN_PERIOD)
    alignVariables(trainingData, testingData)
    normedTrainTestData = normalizeData(trainingData, testingData) #norms non-categoricals only

    if saveVarsFilename != "":
        writeDataFile(trainingData, saveVarsFilename)

    if flagPrintVarStats:
        print "\nTRAINING VARIABLES STATISTICS"
        printVarStats(trainingData)
        print "\nTESTING/RESULTS VARIABLES STATISTICS"
        printVarStats(testingData)
        print "\nRENORMALIZED VARIABLES STATISTICS"
        printVarStats(normedTrainTestData)

    regLow, regHigh = (min(regRange), max(regRange)) # regularization
    if regLow == regHigh:
        regularization = regLow
    else:
        regularization = optimizeRegularization(regLow, regHigh, penalty, trainingData)

    if regSweep != ():
        sweepRegularization(regSweep, penalty, trainingData)

    if flagPrintLRCoef or (outFileName != ""):
        LRModel = makeLogisticRegression(trainingData, regularization, penalty) 
        printLRCoefficients(LRModel, trainingData)

    if outFileName != "":
        testingDataArray = getXData(testingData) # getXData: dict -> array
        testingProbPredictions = LRModel.predict_proba(testingDataArray)
        CLASS_1_COL = 0 # column for class "1" probs (other column is for class "0")
        writePredictions(testingProbPredictions[:,CLASS_1_COL], testingData, outFileName)
    print "\nProgram finished.\n"    

def parseCommandLine():
    # set defaults
    flagPrintVarStats = False
    flagPrintLRCoef = False
    outFileName = ""
    regRange = (0.05, 0.05)
    regSweep = ()
    penalty = 'l2'
    saveVarsFilename = ""
    #
    commandLineArgs = [arg.strip() for arg in sys.argv[1:]]
    commandLineArgs.reverse()
    while len(commandLineArgs) > 0:
        arg = commandLineArgs.pop()  # get next argument
        if arg == "--printvarstats":
            flagPrintVarStats = True
        elif arg == "--printweights":
            flagPrintLRCoef = True
        elif arg == "--predfile":
            outFileName = commandLineArgs.pop()
        elif arg == "--penalty":
            penalty = commandLineArgs.pop()
        elif arg == "--reg":
            reg = float(commandLineArgs.pop())
            regRange = (reg,) # a 1-element tuple
        elif arg == "--regopt":
            regLo = float(commandLineArgs.pop())
            regHi = float(commandLineArgs.pop())
            regRange = (regLo, regHi)
        elif arg == "--savevars":
            saveVarsFilename = commandLineArgs.pop()
        elif arg == "--regsweep":
            regSweepLo = float(commandLineArgs.pop())
            regSweepHi = float(commandLineArgs.pop())
            regSweepN  = int(commandLineArgs.pop())
            regSweep = (regSweepLo, regSweepHi, regSweepN)
        else:
            print "\nCommand line arguments are:"
            print "--printvarstats         print variable stats, ranges, etc"
            print "--printweights          print regression weights"
            print "--predfile  <fname>     predictions filename for output"
            print "--penalty   <l1|l2>     use L1 or L2 regularization penalty"
            print "--reg       <r>         regularization parameter"
            print "--regopt    <r> <r>     find optimum regularization in a range"
            print "--regsweep  <r> <r> <N> reg swept over range in N steps for AUCs"
            print "--savevars <fname>      save training variables to csv file"
            print
            return
    # got args, now go do it!
    doCalculations(flagPrintVarStats,flagPrintLRCoef, \
                    outFileName, saveVarsFilename, regRange, regSweep, penalty)
         
def main():
    parseCommandLine()

main()


# NOTES:
# L1 -- peak at reg=0.0064; AUC = 0.9539, single variable Var74 used
# L2 -- peak at reg=0.0512, AUC = 0.9291


