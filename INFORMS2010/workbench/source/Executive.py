import ProvidedData
from Transforms import *
from Prediction import *
from Optimize   import * 
from InputOutput import * 
from GetClassifier import *
from GetDataTransform import *
import sys

def Execute(    loadFileName=None,  loadDirName=None, \
                classifierName="linregL2", dataTransformName=None, \
                printVarStatsFlag = False,  printClassifierWeightsFlag = False, \
                regDefault = 1.0, regOptRange = None, regSweepRange = None, gamma=None,\
                submissionFileName=None, savePredictionsFileName=None, \
                loadTransformedDataFilename = None, saveTransformedDataFilename=None  ):

    print "\n*** INFORMS 2010 Data Mining Contest Program ***\n"
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
    transformDescriptions  = getDataTransform(dataTransformName, pd) 

    for transformDescription in transformDescriptions:
        transformedData = transformData(transformDescription, xData=loadedData)
        if saveTransformedDataFilename:
            saveTransformedDataFile(transformedData, saveTransformedDataFilename)
        if printVarStatsFlag:
            printVarStats(transformedData)
        optReg = regDefault
        if regSweepRange:
            optReg = sweepRegularization(regSweepRange, classifier, \
                        transformedData, targetVariable, \
                        predictProbs=predictProbsFlag, yPostProcFunc=None )
        if regOptRange:
            optReg = optimizeRegularization(regOptRange, classifier, \
                        transformedData, targetVariable, \
                        predictProbs=predictProbsFlag, yPostProcFunc=None  ) 
        # now we have optimum regularization optReg, so predict using that
        print "Optimum regularization to use:", optReg
        optClassifier = classifier(optReg)
        preds = kFoldPrediction( transformedData, targetVariable, \
                                 optClassifier, predictProbs=predictProbsFlag ) 
        # preds = PostProcessor(preds)   to be implemented??
        auc = AUC(targetVariable, preds)  
        if printClassifierWeightsFlag:
            printClassifierWeights( optClassifier, transformedData)
        print "\nRESULTS:  AUC:",auc, "  Reg:", optReg, 
        print "  Classifier:", classifierName,"  Transform:",dataTransformName,"\n"
        if submissionFileName:
            writeSubmissionFile(timestamps, targetVariable, preds, submissionFileName)
        if savePredictionsFileName:
            savePredictionsFile(preds, savePredictionsFileName)
    print "\nProgram finished.\n"    


def parseCommandLine():

    # set defaults
    loadFileName = None 
    loadDirName = None
    loadTrDataFilename = None 
    saveTrDataFilename = None 
    classifierName = 'linregL2'
    dataTransformName = 'default'
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
            print "--loadpredfile <filename>   load previously saved predictions"
            print "--loadpreddir  <dir>        load all prediction files in directory"
            print "--loadtdata    <filename>   load transformed data from file"
            print ""
            print "--transform    <name>       data transform name to use"
            print "--classifier   <name>       classifier to use"
            print "--reg          <float>      default regularization"
            print "--regopt       <lo,hi>      optimal regularization search in range"     
            print "--regsweep     <lo,hi,N>    sweep regularization in N steps in range"
            print "--gamma        <float>      gamma parameter for SVM & SVR"
            print "--printweights              print classifier weights"
            print "--printvarstats             print variable statistics"
            print ""
            print "--writesub     <filename>   write submission file of predictions"
            print "--savepredfile <filename>   save predictions for later loading"
            print "--savetdata    <filename>   save transformed data to   file"
            print ""
            return

    # got all the arguments set, so now go execute on them! 
    Execute(    loadFileName = loadFileName,  loadDirName = loadDirName, \
                classifierName = classifierName, dataTransformName = dataTransformName, \
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


