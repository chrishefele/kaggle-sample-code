import pickle
import numpy
import os, os.path 
import time

def saveTransformedDataFile(inDataDict, outPathFileName):
    fout = open(outPathFileName, "w")
    pickle.dump(inDataDict,fout)
    fout.close()
    print "Wrote transformed data to:", outPathFileName

def loadTransformedDataFile(inFileName): 
    print "Reading transformed data from:", inFileName 
    fin = open(inFileName, "r")
    transformedData = pickle.load(fin)
    fin.close()
    return transformedData

def savePredictionsFile(predictionsArray, outPathFileName):
    predDict = {}
    outFileName = os.path.basename(outPathFileName)
    predDict["PREDICTIONS."+outFileName] = predictionsArray
    fout = open(outPathFileName, "w")
    pickle.dump(predDict,fout)
    fout.close()
    print "Wrote predictions to:", outPathFileName

def loadPredictionsFile(inFileName): 
    print "Reading predictions from:", inFileName 
    fin = open(inFileName, "r")
    predDict = pickle.load(fin)
    fin.close()
    return predDict

def loadPredictionsDirectory(directoryName):
    assert os.path.isdir(directoryName)
    allPredsDict = {}
    fullDirName = os.path.abspath(directoryName)
    for filename in os.listdir(fullDirName):
        predDict = loadPredictionsFile(os.path.join(fullDirName, filename))
        allPredsDict = dict( allPredsDict.items() + predDict.items() )
    return allPredsDict
   
def writeSubmissionFile( allTimestamps, allTargetVariable, allPredictions, outFileName):
    testMask    = numpy.isnan(allTargetVariable)
    timestamps  = allTimestamps[ testMask]
    predictions = allPredictions[testMask]  
    fout = open(outFileName, "w")
    fout.write("Timestamp,TargetVariable \n")
    for tstamp, pred in zip(timestamps, predictions):
        predString = "%f" % pred    # defaults to 6 digits after decimal point
        outputLine = str(round(float(tstamp),5)) + "," + predString + "\n"
        fout.write(outputLine)
    fout.close()
    print "Wrote submission file to:", outFileName

def printClassifierWeights(classifier, inData):
    print "\nClassifier Weights/Coefficients"
    if "coef_" in dir(classifier): 
        if len(classifier.coef_.shape)>1:
            varWeights = list( classifier.coef_[:] )[0]
        else:
            varWeights = list( classifier.coef_ ) 
        varNames = list(inData.keys())
        varNames.sort() # in predict, columns of data are stacked in sorted varName order
        print "\nSorted by Name\n=============="
        byName = zip(varNames, varWeights)
        for name, weight in sorted(byName):
            print "%+5.5f   %s" % (weight, name)
        print "\nSorted by Weight\n================"
        byWeights = zip(varWeights, varNames)
        for weight, name in sorted(byWeights):
            print "%+5.5f   %s" % (weight, name)        
        print "\n"
    else:
        print " ?? Display of weights/coefs requested, but this classifier provides none.\n"

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
    print "End of Variable Statistics\n"

def localTimeString():
    tm  = time.localtime()
    hr  = "%02d" % tm.tm_hour
    mn  = "%02d" % tm.tm_min
    sec = "%02d" % tm.tm_sec
    tm_str = hr+":"+mn+":"+sec
    return tm_str

