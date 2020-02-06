# Transforms.py
# Functions used to transform raw data into data sent to the classifiers
# e.g. normalize, timeshift, etc. 
#

import numpy
from numpy import array, dot
import scipy.stats
import mdp
import itertools
import sys
import string

def makeGetCategoricalVars(dataSourceFunc):
    def getCategoricalVars(_):
        return dataSourceFunc()
    return getCategoricalVars

def makeGetFloatVars(dataSourceFunc):
    def getFloatVars(_):
        return dataSourceFunc()
    return getFloatVars

def makeGetFloatPriceVars(dataSourceFunc):
    def getFloatPriceVars(_):
        return dataSourceFunc()
    return getFloatPriceVars

def makeGetTimeOfDayFuncTargetVar(timestamps, targetVar, func, tag):
    def getTimeOfDayFuncTargetVar(_):
        outData={}
        trainMask = numpy.isfinite(targetVar)
        trainDayFractions = timestamps[trainMask] - numpy.fix(timestamps[trainMask])
        trainTargetVar = targetVar[trainMask] 
        lookupTable = {}
        for trainDayFraction in set(trainDayFractions):
            trainDayFractionMask = (trainDayFractions == trainDayFraction)
            dayFractionTargetVarFunc = func( trainTargetVar[trainDayFractionMask] ) 
            lookupTable[trainDayFraction] = dayFractionTargetVarFunc
        funcPreds = [lookupTable[dayFrac] for dayFrac in (timestamps-numpy.fix(timestamps))]
        outData[tag] = numpy.array(funcPreds)
        return outData
    return getTimeOfDayFuncTargetVar

def makeGetTimeOfDayMeanTargetVar(timestamps, targetVar):
    return makeGetTimeOfDayFuncTargetVar(timestamps, targetVar, \
                                         numpy.mean, "TARGETPERIODMEAN")

def makeGetTimeOfDayStdTargetVar( timestamps, targetVar):
    return makeGetTimeOfDayFuncTargetVar(timestamps, targetVar, \
                                         numpy.std, "TARGETPERIODSTD")


def _makeGroupByTimestamp(timestamps, timestampGroupingFunc, dataEvalFunc, dataUpdateFunc, tag):
    def groupByTimestamp(inData):
        outData={}
        for varName in inData:
            outData[varName+tag]=numpy.copy(inData[varName])
            tsGroupLabels = timestampGroupingFunc(timestamps)
            for tsGroupLabel in set(tsGroupLabels): 
                groupedData = outData[varName+tag][tsGroupLabels==tsGroupLabel]
                outData[varName+tag][tsGroupLabels==tsGroupLabel] = \
                    dataUpdateFunc(groupedData,dataEvalFunc(groupedData))
        return outData
    return groupByTimestamp

def makeDayCenter(timestamps):
    return _makeGroupByTimestamp(timestamps, (lambda ts: numpy.fix(ts)), \
                                numpy.mean, (lambda x,y: x-y),      "_DAYCENTER")
def makePeriodCenter(timestamps):
    return _makeGroupByTimestamp(timestamps, (lambda ts: ts-numpy.fix(ts)), \
                                numpy.mean, (lambda x,y: x-y),      "_PERIODCENTER")
def makeDayNorm(timestamps):
    return _makeGroupByTimestamp(timestamps, (lambda ts: numpy.fix(ts)), \
                                numpy.std , (lambda x,y: 1.*x/y),   "_DAYNORM")
def makePeriodNorm(timestamps):
    return _makeGroupByTimestamp(timestamps, (lambda ts: ts-numpy.fix(ts)), \
                                numpy.std , (lambda x,y: 1.*x/y),   "_PERIODNORM")
# Note: seems periodNorm +0.0030, works best out of the 4 functions above (the other 3 hurt) 

def _booleanToBinary(b):
    if b:
        return 1
    else:
        return 0 

def _timestampToPeriod(ts):
    #converts from a timestamp string to the integer 0-78 of the 5 minute period
    #in the trading day;  9:30 is 0, and 4pm is 78
    t = float(ts)
    dayFraction = t - int(t) 
    dayPeriod = dayFraction*12*24 - 114
    return int(round(dayPeriod,0))

def makeGetTimeBinVars(timestampsArray):
    # binary 0|1 categorical variable for each 5min bin (except the earliest)
    def getTimeBinVars(_):
        outData = {}
        fiveMinPeriods = [ _timestampToPeriod(ts) for ts in timestampsArray ] 
        colVals = list( set(fiveMinPeriods) - set([min(set(fiveMinPeriods))]) ) #avoid earliest
        for colVal in sorted(colVals): 
            newVals = [ _booleanToBinary(colVal==thisVal) for thisVal in fiveMinPeriods ]
            newVals = numpy.array(newVals)
            newVarName = "Time5MinBin=" + str(colVal) 
            outData[newVarName] = newVals
        return outData
    return getTimeBinVars

def passthruVars(inData):
    outData={}
    for varName in inData:
        outData[varName+""] = numpy.copy(inData[varName])
    return outData

def centerMean(inData):
    outData={}
    for varName in inData:
        outData[varName+"_CTRMEAN"] = inData[varName] -inData[varName].mean()
    return outData

def normStd(inData):
    outData={}
    for varName in inData:
        outData[varName+"_NORMSTD"] = inData[varName] /inData[varName].std()
    return outData

def normCenter(inData):
    return normStd(centerMean(inData))

def normZeroToOne(inData):
    outData={}
    for varName in inData:
        din = inData[varName]
        outData[varName+"_NORM01"] = (din-din.min())/(din.max()-din.min())
    return outData
    
def squareVars(inData):
    outData={}
    for varName in inData:
        outData[varName+"_SQUARE"] = pow( inData[varName],2) 
    return outData

def cubeVars(inData):
    outData={}
    for varName in inData:
        outData[varName+"_CUBE"] = pow(inData[varName],3) 
    return outData
    
def cubicPolynomialVars(inData):
    return pasteColumns( [inData, squareVars(inData), cubeVars(inData)] ) 

def signVars(inData):
    outData={}
    for varName in inData:
        outData[varName+"_SIGN"] = numpy.sign(inData[varName])
    return outData

def entropyOfProbs(inData):
    outData={}
    EPSILON = 1e-10
    for varName in inData:
        p0 = inData[varName]
        p0[ p0>=1.0 ] = 1.0-EPSILON # clamp to be just inside the (0,1) range 
        p0[ p0<=0.0 ] = 0.0+EPSILON
        p1 = 1.0 - p0
        entropy = -(p0*numpy.log2(p0) + p1*numpy.log2(p1))
        outData[varName+"_ENTROPY"] = entropy
    return outData

def percentileVars(inData):
    outData = {}
    for varName in inData:
        varValues = inData[varName]
        l = [ (varVal,index0) for index0, varVal in enumerate(varValues) ]
        l.sort() # sort by values
        l = [ (index0, varVal, index1) for index1, (varVal, index0) in enumerate(l) ]
        l.sort() # sort by original index
        numVals = float(len(l))
        percentileVals = array([ index1/numVals for index0, varVal, index1 in l ])
        outData[varName+"_PERCENTILE"] = percentileVals
    return outData

def percentileToGaussian(inData):
    outData = {}
    percentiles = percentileVars(inData)
    for varName in percentiles: 
        # next line is a HACK; scales to 1%-99% (+/- 2.3stdev), not actual min/max 
        pct = percentiles[varName] *0.99 + +0.005  
        outData[varName+"_%TOGAUSSIAN"] = scipy.stats.norm.ppf( pct ) 
    return outData
    
def makeSelectVars(selectVarsNameList):
    def selectVars(inData):
        outData={}
        for varName in inData:
            if varName in selectVarsNameList:
                outData[varName] = numpy.copy(inData[varName])
        return outData
    return selectVars

def _timeShift(vals, shift):   #to be used only by timeShiftVars below
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

def timeShiftedOnlyVars(inData, shifts = [-2, -1, 1, 2] ):  
    #Note: default function returns only the shifts, not the original variable 
    outData = {}
    # MAX_TIME_SHIFT = defaultShift 
    for varName in inData:
        # for shift in range(-MAX_TIME_SHIFT,-1+1) + range(1,MAX_TIME_SHIFT+1):
        for shift in shifts:
            suffix = "_TIMESHIFT"+str(shift)
            outData[varName + suffix] = _timeShift( inData[varName], shift )
    return outData

def timeShiftVars(inData):  #shifted vars, along with the original vars 
    return pasteColumns( [inData, timeShiftedOnlyVars(inData)] )

def makeMultiTimeShiftVars(timeShiftsList):
    def multiTimeShiftVars(inData):
        return timeShiftedOnlyVars(inData, shifts=timeShiftsList)
    return multiTimeShiftVars

def makeVarSelectLag(varName, lag):
    selectVar = makeSelectVars([varName])
    timeShift = makeMultiTimeShiftVars([lag]) 
    def varSelectLag(inData):
        return timeShift(selectVar(inData))
    return varSelectLag 

# hourMinMaxHighLowPriceVars didn't provide any gains
def hourMinMaxHighLowPriceVars(inData):
    outData = {}
    for varName in inData:
        for varNameSuffix in ["HIGH","LOW"]:
            if varNameSuffix in varName:
                dataLagsList = [_timeShift(inData[varName],shift) for shift in range(0,12+1)]
                dataLags = numpy.column_stack(dataLagsList)
                outData[varName+"_HRMAX"] = dataLags.max(axis=1) # max of the rows
                outData[varName+"_HRMIN"] = dataLags.min(axis=1) # min of the rows
            else:
                pass # placeholder for actions on non-HIGH/LOW variables
    return outData

def appendHourMinMaxHighLowPriceVars(inData):
    return pasteColumns( [ inData, hourMinMaxHighLowPriceVars(inData) ] ) 


def hourSlopeVars(inData):
    outData = {}
    timePts = numpy.arange(0,12+1)
    def slopeWithTime(yPts):
        slope, intercept = numpy.polyfit(timePts,yPts,1)
        return slope
    for varName in sorted(inData):
        print "  Calculating HRSLOPE for:",varName
        sys.stdout.flush()
        dataLagsList = [_timeShift(inData[varName],shift) for shift in range(0,12+1)]
        dataLags = numpy.column_stack(dataLagsList)
        outData[varName+"_HRSLOPE"] = numpy.apply_along_axis(slopeWithTime, 1, dataLags) 
    return outData

def appendHourSlopeVars(inData):
    return pasteColumns([inData, hourSlopeVars(inData)])

def hourCorrVars(inData):
    outData = {}
    timePts = numpy.arange(0,12+1)
    corrWithTime = lambda yPts: numpy.corrcoef(timePts,yPts)[0][1]
    for varName in sorted(inData):
        print "  Calculating HRCORR for:",varName
        sys.stdout.flush()
        dataLagsList = [_timeShift(inData[varName],shift) for shift in range(0,12+1)]
        dataLags = numpy.column_stack(dataLagsList)
        outData[varName+"_HRCORR"] = numpy.apply_along_axis(corrWithTime, 1, dataLags) 
    return outData

def appendHourCorrVars(inData):
    return pasteColumns([inData,hourCorrVars(inData)])


def fullCrossProduct(inData):
    outData={} 
    varNames = inData.keys()
    for varName1, varName2 in itertools.combinations(varNames,2): # pick 2 at a time
        productName = "("+varName1+"_*_"+varName2+")"
        outData[productName] = inData[varName1] * inData[varName2]
    return outData

def makePartialCrossProduct(inDataOne):
    def partialCrossProduct(inDataTwo):
        outData={}
        for varNameOne in inDataOne:
            for varNameTwo in inDataTwo:
                productName = varNameOne+"_*_"+varNameTwo
                outData[productName] = inDataOne[varNameOne] * inDataTwo[varNameTwo]
        return outData
    return partialCrossProduct

def _doComponentAnalysis(inData, componentAnalysisFunc, namePrefix):
    outData = {}
    xData = numpy.column_stack( [inData[varName] for varName in inData] )
    caData = componentAnalysisFunc(xData*1.0)
    inDataVarNames = "{"+string.join(inData.keys(),"&&&")+"}"
    for colNum, colData in enumerate(caData.transpose()):
        outData[namePrefix+str(colNum)+inDataVarNames] = colData
    return outData

def doPCA(inData):
    return _doComponentAnalysis(inData,mdp.pca,"PCA")

def doICA(inData):
    return _doComponentAnalysis(inData,mdp.fastica,"ICA")

def makeDoAnchoredPCA(anchorVarName):
    def doAnchoredPCA(inData):
        anchorVarData = numpy.copy(inData[anchorVarName])
        anchorVarDict = { anchorVarName : anchorVarData } 
        varsToPCA = {} 
        for varName in inData:
            if varName != anchorVarName:
                varData = inData[varName] 
                projOnAnchorVar = anchorVarData * dot(anchorVarData,varData)/ \
                                                  dot(anchorVarData,anchorVarData) 
                varsToPCA[varName] = varData - projOnAnchorVar
        return dict( anchorVarDict.items() + doPCA(varsToPCA).items() )  
    return doAnchoredPCA         

def integrateVars(inData):
    outData={}
    for varName in inData:
        outData[varName+"_INTEGRATED"] = numpy.cumsum(inData[varName])
    return outData

def gradientVars(inData):
    outData={}
    for varName in inData:
        outData[varName+"_GRADIENT"] = numpy.gradient(inData[varName])
    return outData
   
def diffVars(inData):
    outData={}
    for varName in inData:
        outData[varName+"_DIFF"] = numpy.ediff1d(inData[varName], to_begin=0) 
    return outData

# --------------------------------------------------------------------
           
class Memoize:
    # usage: myfunc = Memoize(myfunc) 
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}
    def __call__(self, *args):
        if not self.memo.has_key(args):
            self.memo[args] = self.fn(*args)
        return self.memo[args]

def pasteColumns(inDataList):
    pastedDataCols = {}
    for inData in inDataList:
        pastedDataCols = dict( pastedDataCols.items() + inData.items() ) 
    return pastedDataCols

def composeFunctions(functionList):
    if len(functionList)>=2:
        f0,f1,fRest = functionList[0], functionList[1], functionList[2:]
        def f0f1(x):
            return f0(f1(x))
        return composeFunctions( [f0f1]+fRest ) 
    else:
        f0 = functionList[0]
        return f0

def printTransformDescription(transformDescription, silent=False):
    outString = "["
    for functionGroup in transformDescription:
        outString += "[ " 
        for function in functionGroup:
            outString += function.func_name+" "
        outString += " ]" 
    outString += "]"
    if not silent:
        print "Data Transform Description: ",outString
    return outString

def transformData(transformDescription, xData = None):
    # e.g. transformDescription = [ [f1,f2,f3,srcdatafunc4(None)], [f5,srcdatafunc6(None)]]
    # or   transformDescription = [ [f1,f2,f3,f4(xData)] [f5,f6,f7(xData)] ] 
    printTransformDescription(transformDescription)
    transformedColGroups = \
        [composeFunctions(funcGroup)(xData) for funcGroup in transformDescription]
    return pasteColumns( transformedColGroups )
        




