import sys
sys.path.append("/home/chefele/INFORMS2010/workbench/source")

import ProvidedData
from Transforms import *
from Transforms import _timeShift 
from Prediction import *
from Optimize   import * 
from InputOutput import * 
import InputOutput
from GetClassifier import *
from GetDataTransform import *
import sys


def PriceReturnsGenerator(transformedData):
    # transformedData = a dict of numpy arrays of each stock's price data
    print "Generating Returns from Prices" 
    sys.stdout.flush() 
    for varNum in ProvidedData.VARS_FLOATS: # only floats used, no categoricals  
        varNumNamesFound = []
        varNumNamePrefix = "Variable"+str(varNum)
        PRICE_SUFFIXES  = ["OPEN","HIGH","LOW","LAST","LAST_PRICE"]
        for varNumNameSuffix in PRICE_SUFFIXES:
            varNumName = varNumNamePrefix + varNumNameSuffix
            for trDataVarName in transformedData.keys():
                if varNumName in trDataVarName: 
                    varNumNamesFound.append(trDataVarName)
        for varNumNameStart in set(varNumNamesFound):
            for varNumNameEnd in set(varNumNamesFound):
                for varLag in [0,1]:          # **** HARD CODED LAGS?!?!***
                    startLag =  0 + varLag
                    endLag   = 12 + varLag 
                    startData = _timeShift( transformedData[varNumNameStart],startLag)
                    endData   = _timeShift( transformedData[varNumNameEnd],  endLag)
                    returns = numpy.log10(endData) - numpy.log10(startData)
                    returnsName = varNumNameEnd   + "_LAG"+str(endLag) + "_-_" +\
                                  varNumNameStart + "_LAG"+str(startLag)
                    # print "GENERATED RETURN COMBINATION:", returnsName
                    outData = { returnsName : returns }
                    yield outData

def AllPriceReturns(inData): # inData must be stock prices; returns all variable returns
    outData = {}
    for priceReturn in PriceReturnsGenerator(inData): #returns dict{ varName:varReturn }
        for varName, varReturn in priceReturn.items():
            outData[varName] = varReturn
    return outData
 

def VariableSelection(    loadFileName=None,  loadDirName=None, \
                classifierName="linregL2", dataTransformName="getFloatPriceVars", \
                returnTransformName = "passthruVars", etcReturnsName = None,\
                printVarStatsFlag = False,  printClassifierWeightsFlag = False, \
                regDefault = 1.0, regOptRange = None, regSweepRange = None, gamma=None,\
                submissionFileName=None, savePredictionsFileName=None, \
                loadTransformedDataFilename = None, saveTransformedDataFilename=None  ):

    print "\n*** Variable Selection Program ***\n"
    pd = ProvidedData.ProvidedData()
    targetVariable = pd.getTargetVar()
    timestamps = pd.getTimestamps()

    if loadFileName:
        loadedData = loadPredictionsFile(loadFileName)
    elif loadDirName:
        loadedData = loadPredictionsDirectory(loadDirName)
    elif loadTransformedDataFilename:
        loadedData = loadTransformedDataFile(loadTransformedDataFilename)
    else:
        loadedData = None  # assumes transform loads its own data, as some do

    classifier = getClassifier(classifierName, gamma=gamma)  #returns classifier(reg)  
    predictProbsFlag = getClassifierPredictProbsFlag(classifierName)   
 
    # transform PRICE data before returns are calculated
    transformDescriptions   = getDataTransform(dataTransformName, pd) 
    transformDescription    = transformDescriptions[0] #for getFloatPriceVars
    transformedData         = transformData(transformDescription, xData=loadedData)

    # get other (fixed) returns to be appended to any returns generated from prices
    # (note: etcReturnsDescription *must* provide it's own data source;
    #        also, return cannot loop, see [0]; only first [[][]] transform list used)
    if etcReturnsName: 
        etcReturns = transformData( getDataTransform(etcReturnsName,pd)[0] )
    else:
        etcReturns = {}

    # after returns are compiled, possibly do another transform
    returnTransformDescriptions  = getDataTransform(returnTransformName, pd) 
    returnTransformDescription   = returnTransformDescriptions[0]

    priceReturnVars = [ prDict for prDict in PriceReturnsGenerator(transformedData) ]
    etcVars = [ dict([item]) for item in etcReturns.items() ] 
    trialVars = etcVars + priceReturnVars
    selectedVars= {}
    selectedVarsReport = [] 
    passNum = 0
    thisPassAUC = 0.0 
    deltaAUC    = 1.0 

    while deltaAUC > 0.0001 :   # **** HARD CODED IMPROVEMENT? ADD #PASSES TOO???
        bestTrialAUC = 0.0 
        bestTrialVar = {} 
        passNum += 1 
        for trialVar in trialVars: 
            # do a transform on the calculated returns data (not prices) in trialVar
            # returnDataTransformed = transformData(returnTransformDescription, \
            #                                             xData = trialVar)
            # trialVar = returnDataTransformed
            # *** commented out above two lines 10/1/2010 for PCA ; moved below trialVarCombo

            if set(trialVar.keys()).intersection(set(selectedVars.keys())): 
                print "\nSKIPPING previously selected variable:",trialVar.keys(),"\n"
                continue

            # trialVarCombo = normCenter( dict(selectedVars.items()+trialVar.items()) ) # Worse!
            trialVarCombo =               dict(selectedVars.items()+trialVar.items()) # better
            trialVarCombo = transformData(returnTransformDescription,xData=trialVarCombo) #***
            # *** added above 1 line for PCA 10/1/2010
            
            if printVarStatsFlag:
                printVarStats(trialVarCombo)
            optReg = regDefault
            if regSweepRange:
                optReg = sweepRegularization(regSweepRange, classifier, \
                            trialVarCombo, targetVariable, \
                            predictProbs=predictProbsFlag, yPostProcFunc=None )
            if regOptRange:
                optReg = optimizeRegularization(regOptRange, classifier, \
                            trialVarCombo, targetVariable, \
                            predictProbs=predictProbsFlag, yPostProcFunc=None  ) 
            # now we have optimum regularization optReg, so predict using that
            print "Optimum regularization to use:", optReg
            optClassifier = classifier(optReg)
            preds = kFoldPrediction( trialVarCombo, targetVariable, \
                                     optClassifier, predictProbs=predictProbsFlag ) 
            # preds = PostProcessor(preds)   to be implemented??

            auc = AUC(targetVariable, preds) 
 
            if printClassifierWeightsFlag:
                printClassifierWeights( optClassifier, trialVarCombo)
            print "\nRESULTS:  AUC:",auc, "  Reg:", optReg, 
            print "  Classifier:", classifierName,"  Transform:",dataTransformName,"\n"

            if auc > bestTrialAUC:
                bestTrialAUC = auc
                bestTrialVar = trialVar
                print "NEW_MAX_AUC:", bestTrialAUC, 
                print "DELTA_AUC:", bestTrialAUC-thisPassAUC,
                print "CLASSIFIER:", classifierName,
                print "N_VARS:",len(trialVarCombo.keys())
                print "NEW_MAX_VARS:", sorted(trialVarCombo.keys())
                passPrefix = "pass"+ ("%03i" % passNum)+"_"
                if submissionFileName:
                    writeSubmissionFile(timestamps, targetVariable, preds, \
                                                passPrefix + submissionFileName)
                if savePredictionsFileName:
                    savePredictionsFile(preds, \
                                                passPrefix + savePredictionsFileName)
                if saveTransformedDataFilename:
                    saveTransformedDataFile(trialVarCombo, \
                                            passPrefix + saveTransformedDataFilename)
        # /for
        # now have best candidate to add, so add it to the selected list 
        selectedVars = dict( selectedVars.items() + bestTrialVar.items() ) 
        bestTrialVarName = bestTrialVar.keys()[0]
        selectedVarsReport.append( (bestTrialAUC,bestTrialVarName) ) 
        lastPassAUC = thisPassAUC
        thisPassAUC = bestTrialAUC
        deltaAUC = thisPassAUC - lastPassAUC 
        print "\nPASS AUC_IMPROVEMENT:", deltaAUC, 
        print "AUC:", thisPassAUC,
        print "CLASSIFIER:", classifierName,
        print "TIME:", InputOutput.localTimeString()
        print "SELECTED VARIABLES AFTER THIS PASS:"
        #for selectedVarName in selectedVars:
        #    print "  ",selectedVarName
        #print
        for passNum, (selectedVarAUC, selectedVarName) in enumerate(selectedVarsReport):
            print "PASS:", passNum, "AUC:",selectedVarAUC, selectedVarName
        print 
    # /while
    print "\nProgram finished.\n"    


def parseCommandLine():

    # set defaults
    loadFileName = None 
    loadDirName = None
    loadTrDataFilename = None 
    saveTrDataFilename = None 
    classifierName = 'linregL2'
    dataTransformName = 'getFloatPriceVars'
    returnTransformName = 'passthruVars'
    etcReturnsName = None
    printVarStatsFlag = False
    regDefault = 1.0 
    regOptRange = None
    regSweepRange = None
    gamma = None
    printClassifierWeightsFlag = False
    submissionFileName = None
    savePredictionsFileName = None 
    #
    commandLineArgs = [arg.strip() for arg in sys.argv[1:]]
    commandLineArgs.reverse()
    while len(commandLineArgs) > 0:
        arg = commandLineArgs.pop()  # get next argument
        if arg == "--loadpredfile":
            loadFileName = commandLineArgs.pop() 
        elif arg == "--loadpreddir":
            loadDirName = commandLineArgs.pop() 
        elif arg == "--loadtdata":
            loadTrDataFilename = commandLineArgs.pop()
        elif arg == "--savetdata":
            saveTrDataFilename = commandLineArgs.pop()
        elif arg == "--classifier":
            classifierName = commandLineArgs.pop()
        elif arg == "--transform":
            dataTransformName = commandLineArgs.pop()
        elif arg == "--etcreturntransform":
            etcReturnsName = commandLineArgs.pop()
        elif arg == "--returntransform":
            returnTransformName = commandLineArgs.pop()
        elif arg == "--printvarstats":
            printVarStatsFlag = True
        elif arg == "--printweights":
            printClassifierWeightsFlag = True
        elif arg == "--writesub":
            submissionFileName = commandLineArgs.pop()
        elif arg == "--savepredfile":
            savePredictionsFileName = commandLineArgs.pop()
        elif arg == "--gamma":
            gamma = float(commandLineArgs.pop())
        elif arg == "--reg":
            regDefault = float(commandLineArgs.pop())
        elif arg == "--regopt":
            regLo = float(commandLineArgs.pop())
            regHi = float(commandLineArgs.pop())
            regOptRange = (regLo, regHi, 0)
        elif arg == "--regsweep":
            regSweepLo = float(commandLineArgs.pop())
            regSweepHi = float(commandLineArgs.pop())
            regSweepN  = int(commandLineArgs.pop())
            regSweepRange = (regSweepLo, regSweepHi, regSweepN)
        else:
            print ""
            print "Command line arguments are:"
            print ""
            #print "--loadpredfile <filename>   load previously saved predictions"
            #print "--loadpreddir  <dir>        load all prediction files in directory"
            print "--loadtdata    <filename>   load transformed data from file"
            print ""
            print "--transform    <name>       transform on price data before calc returns"
            print "--etcreturntransform <name> transform making additional returns to trial"
            print "--returntransform <name>    transform applied to trial returns" 
            print "--classifier   <name>       classifier to use"
            print "--reg          <float>      default regularization"
            print "--regopt       <lo,hi>      optimal regularization search in range"     
            print "--regsweep     <lo,hi,N>    sweep regularization in N steps in range"
            print "--gamma        <float>      gamma parameter for SVM & SVR"
            print "--printweights              print classifier weights"
            print "--printvarstats             print variable statistics"
            print ""
            print "--writesub     <filename>   write submission file of best predictions"
            #print "--savepredfile <filename>   save predictions for later loading"
            print "--savetdata    <filename>   save best transformed data to file"
            print ""
            return

    # got all the arguments set, so now go execute on them! 
    VariableSelection(    loadFileName = loadFileName,  loadDirName = loadDirName, \
                classifierName = classifierName, dataTransformName = dataTransformName, \
                returnTransformName = returnTransformName,\
                etcReturnsName = etcReturnsName, \
                printVarStatsFlag = printVarStatsFlag,  \
                printClassifierWeightsFlag = printClassifierWeightsFlag, \
                regDefault = regDefault, regOptRange = regOptRange, \
                regSweepRange = regSweepRange, gamma = gamma,\
                submissionFileName = submissionFileName, \
                savePredictionsFileName = savePredictionsFileName, \
                loadTransformedDataFilename = loadTrDataFilename,  \
                saveTransformedDataFilename = saveTrDataFilename  )
        
def main():
    parseCommandLine()

if __name__ == "__main__":
    main()


