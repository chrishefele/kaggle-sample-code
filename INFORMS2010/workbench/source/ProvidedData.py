# Provided Data object reads, parses and cleans up the original data files,
# resulting in data that can be retrieved with the "get" methods at the end
# and provided to the classifiers (perhaps after intermediate transformations)
# Training & testing data are concatenated arrays kept in a dict, indexed by variable name
# i.e.  dict{ variable_name: array( training_data | test_data ) } 
# Timestamps and target variable are kept in seperate arrays (i.e. not in the dicts).

import numpy
from numpy import array
import sys

TESTING_FILE  = "/home/chefele/INFORMS2010/data/ResultData.csv"
TRAINING_FILE = "/home/chefele/INFORMS2010/data/TrainingData.csv"

VARS_POSSIBLE_INTS = set(range(143,155+1)+range(161,163+1)+[142])
VARS_POSSIBLE_FLOATS = set( [156]+[157,159,160,164,165]+ \
                                range(167,180+1)+range(8,141+1))

VARS_MISSING_INTS = set([156]) # result range > training range, so make it a float
VARS_MISSING_FLOATS = set([ 16,39,66,67,75,84,96,104,106,110,118,\
                                119,122,128,131,132,134,135,138,140])

VARS_INTS   = VARS_POSSIBLE_INTS    - VARS_MISSING_INTS     
VARS_FLOATS = VARS_POSSIBLE_FLOATS  - VARS_MISSING_FLOATS 

# RETURN_PERIOD = 12 # calc stock returns over this many 5min periods (12*5min=1hr)

# =============================================================================

class ProvidedData():

    def readDataFile(self,filename):
        print "Reading:", filename," . . . ",
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
        print "Done."
        sys.stdout.flush()
        return inData

    def isNumber(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def floatWithDefault(self,valString, valIfNotNumber):
        if self.isNumber(valString):
            return float(valString)
        else:
            return float(valIfNotNumber)

    def replaceZero(self,x,zeroReplacement):
        if x==0.0:
            return zeroReplacement
        else:
            return x 

    def numUniqVals(self,strList):
        return len( set(strList) - set(["","-"]) ) 

    def meanNonMissingFloatVals(self,strList):
        floatVals = array( [float(s) for s in strList if self.isNumber(s)] )
        return floatVals.mean()

    def booleanToBinary(self,b):
        if b:
            return 1
        else:
            return 0 

    def timeShift(self,vals, shift): 
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
            
    def fillDataGaps(self, inVals):
        avg = self.meanNonMissingFloatVals(inVals)
        newVals = [ self.floatWithDefault(s,avg) for s in inVals ] # missing data -> avg
        newVals = [ self.replaceZero(x, avg) for x in newVals ] # 0's -> avg (for var22) 
        newVals = numpy.array(newVals)
        return newVals

    def endOfDayPrices(self, dayPrices, tStamps, eodPeriod):   
        # Note: dayPrices should NOT be timeshifted; it must align with timestamps
        dayStamps = numpy.fix(tStamps)
        eodPrices = numpy.copy(dayPrices) # will be overwritten with right values below
        for dayStamp in set(dayStamps): 
            todaysPrices = dayPrices[dayStamps==dayStamp]
            assert (eodPeriod==-1 or eodPeriod==-2) # -2 = 3:55-4:00, -1 = 4:00-9:30
            endOfDayPrice = todaysPrices[eodPeriod]  
            eodPrices[dayStamps==dayStamp] = endOfDayPrice # overwrites 
        return eodPrices

    def makeFloatPriceVars(self, inData):
        print "Making float price variables (not float returns)"
        outData = {}
        for varFloat in VARS_FLOATS:          
            varPrefix = "Variable"+str(varFloat)
            for suffix in ["OPEN","HIGH","LOW","LAST","LAST_PRICE"]:
                varName = varPrefix + suffix
                if varName in inData:
                    priceData = self.fillDataGaps(inData[varName])
                    if numpy.min(priceData) != numpy.max(priceData):  # skip constants 
                        outData[varName] = priceData 
        return outData

    def makeFloatVars(self, inData, returnPeriods, tStamps, \
                            allowMultidayReturns=True, eodPeriod = -1):
        print "Making float variables"
        outData = {}
        # for floating-point variables (e.g. mostly stock prices, some other data too)
        for varFloat in VARS_FLOATS:          
            varPrefix = "Variable"+str(varFloat)
            # special case for Variable 74 -- include raw prices too
            if varPrefix == "Variable74":
                for suffix in ["OPEN","HIGH","LOW","LAST_PRICE"]:
                    outData[varPrefix+suffix] = \
                        self.fillDataGaps(inData[varPrefix+suffix])
            # Vary return calculation (if necessary) by variable type            
            if (varPrefix+"LAST_PRICE") in inData:
                lastPrices = self.fillDataGaps(inData[varPrefix+"LAST_PRICE"])
                openPrices = self.fillDataGaps(inData[varPrefix+"OPEN"])
                timeShiftedLastPrices = self.timeShift(lastPrices, returnPeriods)
                timeShiftedOpenPrices = self.timeShift(openPrices, returnPeriods)
                #Note: Last-to-last, not open-to-last, or open-open, seems to work best 
                theReturn = numpy.log10(timeShiftedLastPrices) - numpy.log10(lastPrices)
                #theReturn = numpy.log10(timeShiftedOpenPrices) - numpy.log10(openPrices)
                #theReturn = numpy.log10(timeShiftedLastPrices) - numpy.log10(openPrices)
                # Note: best AUCs when returns span days, so this 'if' clause has no benefit
                if not allowMultidayReturns: # ...then correct theReturn in the last hour
                    eodLastPrices = self.endOfDayPrices(lastPrices, tStamps, eodPeriod)
                    eodOpenPrices = self.endOfDayPrices(openPrices, tStamps, eodPeriod)
                    dayFractions = tStamps - numpy.fix(tStamps)
                    THREE_PM_DAYFRACTION = (12.+3.)/24.
                    lastHourMask = ( dayFractions >= THREE_PM_DAYFRACTION )
                    theReturn[lastHourMask] = numpy.log10(eodLastPrices[lastHourMask]) - \
                                              numpy.log10(lastPrices[lastHourMask]   )
                    #theReturn[lastHourMask] = numpy.log10(eodOpenPrices[lastHourMask]) - \
                    #                          numpy.log10(openPrices[lastHourMask]   )
                    #theReturn[lastHourMask] = numpy.log10(eodLastPrices[lastHourMask]) - \
                    #                          numpy.log10(openPrices[lastHourMask]   )
                outData[varPrefix+"_LASTLASTRETURN"] = theReturn
            elif (varPrefix+"LAST") in inData:
                lastVals = self.fillDataGaps(inData[varPrefix+"LAST"])
                timeShiftedLastVals = self.timeShift(lastVals, returnPeriods)
                lastToLastReturn = numpy.log10(timeShiftedLastVals) - numpy.log10(lastVals)
                outData[varPrefix+"_LASTLASTRETURN"] = lastToLastReturn
            elif (varPrefix+"OPEN") in inData:
                openVals = self.fillDataGaps(inData[varPrefix+"OPEN"])
                timeShiftedOpenVals = self.timeShift(openVals, returnPeriods)
                openToOpenReturn = numpy.log10(timeShiftedOpenVals) - numpy.log10(openVals)
                outData[varPrefix+"_OPENOPENRETURN"] = openToOpenReturn
            else:
                raise UserWarning("Cannot find variable with prefix "+varPrefix)
        return outData
                
    def makeIntVars(self,inData):
        print "Making categorical / integer variables"
        outData = {}
        # for integer/categorical variables (e.g. not stock prices)
        for varInt in VARS_INTS:
            varName = "Variable"+str(varInt)+"LAST"
            inVals = inData[varName]
            # now add new 0|1 column for each non-missing value/category
            colVals = set(inVals) - set([""])  # don't need a missing ("") value category
            for colVal in colVals: 
                newVals = [ self.booleanToBinary(colVal==thisVal) for thisVal in inVals ]
                newVals = numpy.array(newVals)
                newVarName = varName + "=" + colVal
                outData[newVarName] = newVals
        return outData

    def alignVariables(self,trainingData, testingData):
        # Delete any variables that training has that test doesn't, or vice-versa
        # (except that training data keeps "TargetVariable")
        # Categorical variables that were the problem were: 
        # 'Variable142LAST=-', 'Variable155LAST=4', 'Variable153LAST=8', 
        # 'Variable150LAST=1', 'Variable153LAST=3
        print "Aligning Variables in training & testing data"
        inTrainNotTest = set(trainingData.keys()) - set(testingData.keys())
        inTestNotTrain = set(testingData.keys())  - set(trainingData.keys())
        for varName in inTrainNotTest:
            del trainingData[varName]
        for varName in inTestNotTrain:
            del testingData[ varName]
        inTrainNotTest = set(trainingData.keys()) - set(testingData.keys())
        inTestNotTrain = set(testingData.keys())  - set(trainingData.keys())
        #print "Variables only in Training data:", inTrainNotTest
        #print "Variables only in Testing  data:", inTestNotTrain   
        #print "Finished aligning variables"

    def makeTimestamps(self,inData):
        return numpy.array([ float(ts) for ts in inData["Timestamp"] ]) 

    def makeTargetVariable(self,inData):
        return numpy.array([ float(ts) for ts in inData["TargetVariable"] ])

    def makeMergedTrainTestData(self, allowMultidayReturns=True, \
                                      returnPeriod=12, eodPeriod=-1):
        rawTrainingData = self.readDataFile(TRAINING_FILE)
        rawTestingData  = self.readDataFile(TESTING_FILE)
        #
        trainingTimestamps = self.makeTimestamps(rawTrainingData)
        testingTimestamps = self.makeTimestamps(rawTestingData)
        self.timestamps = numpy.concatenate((trainingTimestamps, testingTimestamps))
        #
        trainingFloatData = self.makeFloatVars(rawTrainingData, returnPeriod,\
                            trainingTimestamps, 
                            allowMultidayReturns = allowMultidayReturns, eodPeriod = eodPeriod)
        testingFloatData  = self.makeFloatVars(rawTestingData , returnPeriod,\
                            testingTimestamps,  
                            allowMultidayReturns = allowMultidayReturns, eodPeriod = eodPeriod)
        trainingIntData = self.makeIntVars(rawTrainingData)
        testingIntData  = self.makeIntVars(rawTestingData )
        trainingFloatPriceData = self.makeFloatPriceVars(rawTrainingData)
        testingFloatPriceData  = self.makeFloatPriceVars(rawTestingData)
        #
        self.alignVariables(trainingFloatData, testingFloatData)
        self.alignVariables(trainingIntData,   testingIntData)
        self.alignVariables(trainingFloatPriceData, testingFloatPriceData)

        assert (trainingFloatData.keys() == testingFloatData.keys())
        assert (trainingIntData.keys() == testingIntData.keys())
        assert (trainingFloatPriceData.keys() == testingFloatPriceData.keys())

        self.floatData = {}
        for varName in trainingFloatData: 
            self.floatData[varName] = numpy.concatenate((trainingFloatData[varName],\
                                                         testingFloatData[varName]))
        self.intData = {}
        for varName in trainingIntData:
            self.intData[varName]   = numpy.concatenate((trainingIntData[varName],\
                                                         testingIntData[varName]))
        self.floatPriceData = {}
        for varName in trainingFloatPriceData:
            self.floatPriceData[varName] = numpy.concatenate(( \
                                           trainingFloatPriceData[varName],\
                                           testingFloatPriceData[varName]))

        trainingTargetVar = self.makeTargetVariable(rawTrainingData)
        testingTargetVar = numpy.zeros(len(testingTimestamps)) + numpy.nan  # unknowns->NaN
        self.targetVar = numpy.concatenate((trainingTargetVar, testingTargetVar))
        self.trainMask = numpy.isfinite(self.targetVar)
        self.testMask =  numpy.isnan(self.targetVar)
       
    def getFloatData(self):
        return self.floatData

    def getFloatPriceData(self):
        return self.floatPriceData

    def getIntData(self):
        return self.intData

    def getTimestamps(self):
        return self.timestamps

    def getTargetVar(self):
        return self.targetVar

    def getTrainMask(self):
        return self.trainMask

    def getTestMask(self):
        return self.testMask

    def __init__(self, allowMultidayReturns = True, returnPeriod = 12, eodPeriod = -1):
        self.makeMergedTrainTestData( allowMultidayReturns = allowMultidayReturns, \
                                      returnPeriod = returnPeriod, eodPeriod = eodPeriod)



