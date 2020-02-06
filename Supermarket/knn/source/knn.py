# KNN for dunnhumbys Shopper Challenge on Kaggle.com 
# (For details, see http://www.kaggle.com/c/dunnhumbychallenge)
# Created 8/5/2011 by Chris Hefele

import numpy
import datetime
import time
import sys
import pickle
import os
import math
import cProfile
import random 
import argparse # included in python 2.7 & later, but works with 2.6

FILE_TEST_CSV    = "/home/chefele/Supermarket/download/test.csv"
FILE_TRAIN_CSV   = "/home/chefele/Supermarket/download/training.csv"
FILE_TEST_CACHE  = "/home/chefele/Supermarket/knn/data/test.cache"     # parsed .CSV, loads fast
FILE_TRAIN_CACHE = "/home/chefele/Supermarket/knn/data/training.cache" # parsed .CSV, loads fast

T_MIN_DATE   = "2010-04-01"  # earliest date in dataset 
T_MAX_DATE   = "2011-06-19"  # latest   date in dataset 
T_TEST_START = "2011-04-01"  # start of test period
T_TEST_END   = T_MAX_DATE    # end of test period 

NO_SALE    = numpy.NaN # Sentinel in arrays for no spending or visit on a date 
PRICE_TOLERANCE = 10   # Prediction is correct if within $10 of actual

XVAL_N_TRAIN = 90000 # default number of custIds sampled from train for cross-validation
XVAL_N_TEST  = 10000 

RAND_SEED  = 1234567
PRINT_MOD  = 20000
DATA_ROW_SIZE = None   # Temporary; shown here for clarity; defined below

# Some small but useful helper functions...

def noSales(xArray):    # boolean mask used to select days with no sales 
    return  numpy.isnan(xArray)

def justSales(xArray):  # boolean mask used to select days with sales  
    return ~numpy.isnan(xArray)

def justSalesFunc(xArray, func, submask=True): # apply function to (subset of) sales data 
    return func( xArray[ justSales(xArray) & submask] )

def geometricMean(xArray):
    return numpy.exp(numpy.mean(numpy.log(xArray))) # TODO add 1 cent to avoid log(0) 

def RMS(xArray):
    return numpy.sqrt( numpy.mean( xArray*xArray ) ) 

def earliestNonZeroIndex(xArray):
    return numpy.nonzero( 1*xArray )[0][0]  #earliest = leftmost 

def dateObj(dateString):
    return datetime.datetime.strptime(dateString,"%Y-%m-%d") 

def dayNum(dateString):  # convert date to array index 
    deltaObj = dateObj(dateString) - dateObj(T_MIN_DATE) 
    return int(deltaObj.days) 

def dateString(day_num): 
    int_day_num = 1*int(day_num) # need to convert any numpy.int -> int for timedelta 
    day_num_date = dateObj(T_MIN_DATE) + datetime.timedelta(int_day_num)
    return day_num_date.strftime("%Y-%m-%d")

DATA_ROW_SIZE = dayNum(T_MAX_DATE) - dayNum(T_MIN_DATE) + 1 
TEST_PERIOD_MASK  = (numpy.array(xrange(0,DATA_ROW_SIZE)) - dayNum("2011-04-01")) >=0
TRAIN_PERIOD_MASK = ~TEST_PERIOD_MASK

BEFORE_HOLIDAYS_MASK = (numpy.array(xrange(0,DATA_ROW_SIZE)) - dayNum("2010-11-07")) <= 0  
AFTER_HOLIDAYS_MASK  = (numpy.array(xrange(0,DATA_ROW_SIZE)) - dayNum("2011-01-03")) >= 0
NO_HOLIDAYS_MASK = BEFORE_HOLIDAYS_MASK | AFTER_HOLIDAYS_MASK

# --------------------------------------------------------------------

def readDataFile(fname):  # read & parse the text/.csv data file 
    print "Reading:", fname
    fin = open(fname,"r")
    header = fin.readline()
    dataRows = {}
    numRows = 0
    for line in fin:
        cust_id, visit_date,   visit_spend = tuple(line.split(","))
        cust_id, visit_daynum, visit_spend = \
                    (int(cust_id), int(dayNum(visit_date)), float(visit_spend))
        if cust_id not in dataRows:
            dataRows[cust_id] = numpy.empty(DATA_ROW_SIZE, dtype=numpy.float) 
            dataRows[cust_id].fill( NO_SALE ) 
        dataRows[cust_id][visit_daynum] = visit_spend
        numRows += 1
        if numRows % PRINT_MOD == 0:
            print numRows,
            sys.stdout.flush()
    print
    return dataRows

def readDataFileCache(csv_file, cache_file):
    if not os.path.exists(cache_file):  # cache_file = saved pre-parsed datafile for speed 
        print "Cache file not found:", cache_file
        rows = readDataFile(csv_file)
        fout = open(cache_file,"wb")
        pickle.dump(rows, fout, pickle.HIGHEST_PROTOCOL)
        fout.close()
        print "Saved data to cache file:", cache_file
    print "Reading:", cache_file
    fin = open(cache_file,"rb")
    rows = pickle.load(fin)
    fin.close()
    return rows

def calcWeightRow(decayDays):
    daysFromTestStart = numpy.array(xrange(DATA_ROW_SIZE)) - dayNum(T_TEST_START)
    weightRow = numpy.exp(1.0*daysFromTestStart/decayDays) # time-decay wts vs time to test
    weightRow[ daysFromTestStart >=0 ] = 0  # don't use data after test period start
    return weightRow


class NearestCustIdsEngine:  
 
    def _addLookupEntries(self, xRows, custCenterFunc):  # initializes lookup tables
        for custId in xRows.keys():   
            self.justSalesCenter[custId] = justSalesFunc( xRows[custId], custCenterFunc,   \
                                            submask=(TRAIN_PERIOD_MASK & NO_HOLIDAYS_MASK) ) 
            self.noSales[custId]   = noSales(xRows[custId])
            self.justSales[custId] = justSales(xRows[custId])

    def __init__(self,  testRows, trainRows, weightRow, custCenterFunc, predReduceFunc, dayknn):
        print "Initializing NearestCustIdsEngine"
        self.testRows  = testRows
        self.trainRows = trainRows
        self.weightRow = weightRow 
        self.custCenterFunc = custCenterFunc # defines center of a row's sales distribution
        self.predReduceFunc = predReduceFunc # calcs predicted sale from N neighbor sales
        self.dayknn = dayknn 
        self.last_testCustId = None

        # Initialize & precompute 3 lookup tables for speed 
        self.justSalesCenter= {}
        self.noSales = {}
        self.justSales = {}
        self._addLookupEntries(self.testRows,  self.custCenterFunc )
        self._addLookupEntries(self.trainRows, self.custCenterFunc)
    
    def makePredictor(self, forTestCustId, usingTrainCustId): 
        # Scale up/down a cust's training sales data so that
        # its mean|median matches test's mean|median
        trainScale = 1.0 * self.justSalesCenter[forTestCustId] / \
                           self.justSalesCenter[usingTrainCustId]  
        predictor = numpy.copy( self.trainRows[usingTrainCustId] )
        justSalesMask = self.justSales[usingTrainCustId] 
        justSalesPredictor = trainScale * predictor[justSalesMask]  
        # justSalesPredictor[ justSalesPredictor < PRICE_TOLERANCE ] = PRICE_TOLERANCE # TODO remove? 
        predictor[justSalesMask] = justSalesPredictor 
        return predictor 

    def _calcDistance(self, testCustId, trainCustId):

        # For distance, use a weighted variant of the Matthew's Correlation Coefficient (MCC)
        # between training data (the predictors) and test data (the actuals).
        # To do that, one must first calculate the confusion matrix, i.e. 
        # tp=true positives, tn=true negatives, fp=false positives, fn=false negatives
        tn = numpy.sum(self.weightRow[ self.noSales[testCustId]   & self.noSales[trainCustId]   ])
        fn = numpy.sum(self.weightRow[ self.justSales[testCustId] & self.noSales[trainCustId]   ])
        fp = numpy.sum(self.weightRow[ self.noSales[testCustId]   & self.justSales[trainCustId] ])
        tp = numpy.sum(self.weightRow[ self.justSales[testCustId] & self.justSales[trainCustId] ])

        # Next, some true positives predict sales >$10 away from actual sales,
        # so we have to move those true-positive sales to false-positives
        predictions = self.makePredictor(testCustId, trainCustId)
        actuals     = self.testRows[testCustId] 
        tp_mask = self.justSales[testCustId] & self.justSales[trainCustId] 
        bad_tp_mask = abs( predictions[tp_mask] - actuals[tp_mask] ) > PRICE_TOLERANCE 
        bad_tp_weights = numpy.sum(self.weightRow[tp_mask][bad_tp_mask]) 
        tp -= bad_tp_weights
        fp += bad_tp_weights

        try:
            mcc = (tp*tn - fp*fn) / math.sqrt( (tp+fp)*(tp+fn)*(tn+fp)*(tn+fn) )
        except ZeroDivisionError: # /0 possible for constant predictions
            mcc = 0.0
        return mcc

    def calcNearestNeighbors(self, testCustId, nTrainCustIds=None):
        # Returns sorted list: [(closest distance, trainCustId), (distance,trainCustId)...]
        # Defaults to returning the full list if just called with testeCustId only 
        if self.last_testCustId == testCustId: # check if we can use cached results
            return self.dists[0:nTrainCustIds] 
        # If here, we switched to a new test customer, so need to compute all new distances
        self.last_testCustId = testCustId
        self.dists = []
        for trainCustId in self.trainRows:  # most program time is spent in this loop
            dist = self._calcDistance(testCustId, trainCustId)
            self.dists.append( (dist, trainCustId) ) 
        self.dists.sort() 
        self.dists.reverse() # assumes larger dist means closer, as with MCC
        return self.dists[0:nTrainCustIds]

    def makePrediction(self, testCustId, kNeighbors): 
        # For each nearest neighbor customer, find their first visit in the test period. 
        # Tabulate the counts of these first-visit days & their respective predicted sales. 
        # Pick the most popular day & estimate the predicted sale using only that day's sales. 
        dayCounts = numpy.zeros(DATA_ROW_SIZE, dtype=numpy.int)
        predSales = {} 
        # If  dayknn, the loop below ensures at least kNeighbors on the date that's picked 
        # if ~dayknn, there will be kNeighbors distributed across the test period dates.
        if self.dayknn:
            nbrs = self.calcNearestNeighbors(testCustId) # returns all neighbors
        else:
            nbrs = self.calcNearestNeighbors(testCustId, kNeighbors) # retuns K neighbors

        for (nbrDist, nbrCustId) in nbrs:
            nbrVisits = TEST_PERIOD_MASK & justSales(self.trainRows[nbrCustId])
            if numpy.any(nbrVisits): 
                day_ix = earliestNonZeroIndex( 1*nbrVisits ) # first nbr visit in test period 
                dayCounts[day_ix] += 1
                if day_ix not in predSales:
                    predSales[day_ix] = numpy.empty(0)
                nbrPreds  = self.makePredictor(testCustId, nbrCustId ) 
                predSales[day_ix] = numpy.append( predSales[day_ix], nbrPreds[day_ix] ) 
                if dayCounts.max() >= kNeighbors: 
                    break
            else:
                pass
                # print "WARNING: Training CustID", nbrCustId, 
                # print "had no visits in the test period\n"

        predDayNum = earliestNonZeroIndex( dayCounts==dayCounts.max() )
        if predDayNum > 0:
            predSale = self.predReduceFunc( predSales[predDayNum] )
        else: # unusual: can't find any sales in TEST period for the neighbors 
            predSale = 0.0  # use global average sale here?
        if predSale < PRICE_TOLERANCE:
            predSale = PRICE_TOLERANCE
        
        if False:
            print "[makePrediction]\n"
            print "TestCustId          :", testCustId
            print "Predicted DayNum    :", predDayNum
            print "Predicted Date      :", dateString(predDayNum)
            print "First Visit Counts  :\n", dayCounts[TEST_PERIOD_MASK][0:],"\n"
            print "First Visits on Date:", len(predSales[predDayNum]) 
            print "Predicted Sale      :", predSale
            sortedSales = numpy.array_str(numpy.sort(predSales[predDayNum]), precision=2)
            print "Predicted Sales:\n", sortedSales
            print "\n[/makePrediction]\n"

        return (dateString(predDayNum), predSale)  

# /class NearestCustIdsEngine 


def makeCrossValidationData(train, nTrainSamples, nTestSamples):
    print "Making cross validation data sets"
    # for X-validation, make a new, sampled test&train set from the original training set 
    trainCustIds = train.keys()
    # random.seed(RAND_SEED) 
    assert nTrainSamples+nTestSamples <= len(train) # prevents shared custIds btw test/train
    samples = random.Random(RAND_SEED).sample(trainCustIds, nTrainSamples + nTestSamples)
    trainSampleCustIds = samples[0:nTrainSamples]
    testSampleCustIds  = samples[nTrainSamples:]
    # 
    trainXVal = {}
    for cid in trainSampleCustIds:
        trainXVal[cid] = train[cid]
    testXVal = {}
    for cid in testSampleCustIds:
        cidVisits = TEST_PERIOD_MASK & justSales(train[cid])
        if numpy.any(cidVisits):
            testXVal[cid] = train[cid]
        else:
            print "WARNING: Excluding custID", cid,
            print "from X-validation data (no visits in the test period)"
    return (trainXVal, testXVal)

def makeCrossValidationAnswers(testXVal): 
    print "Making cross validation answers"
    answers = {}
    for cid in testXVal:
        cidVisits = TEST_PERIOD_MASK & justSales(testXVal[cid])
        if numpy.any(cidVisits): 
            day_ix = earliestNonZeroIndex( 1*cidVisits ) # first visit in test period 
            predDate = dateString(day_ix)
            predSales = testXVal[cid][day_ix]
            answers[cid] = (predDate, predSales)
        else:
            print "WARNING: Excluding custID", cid,
            print "from X-validation answers (no visits in the test period)"
    return answers


class PerformanceTracker:
    def __init__(self, testXVal, testXValAnswers, engine, kNN):
        self.testXVal = testXVal 
        self.testXValAnswers = testXValAnswers
        self.engine = engine 
        self.kNN = kNN 
        self.dateMatches  = 0
        self.salesMatches = 0
        self.dateSalesMatches = 0
        self.numPredictions= 0 
        self.last_custId = None 
        self.matchFlags= { (True, True ):"D+S+", (True, False):"D+S-", \
                           (False,True ):"D-S+", (False,False):"D-S-"  }

    def pctString(self, num, denom):
        return "%5.2f" % (100.0*num/denom)

    def addPrediction(self, custId):
        self.last_custId = custId 
        (actualDate, actualSales) = self.testXValAnswers[custId]
        (predDate,   predSales  ) = self.engine.makePrediction(custId, self.kNN)
        self.numPredictions += 1 
        dateMatch  = (actualDate==predDate)
        salesMatch = abs(predSales-actualSales) < PRICE_TOLERANCE
        if dateMatch:
            self.dateMatches += 1
        if salesMatch:
            self.salesMatches += 1
        if dateMatch and salesMatch:
            self.dateSalesMatches += 1

        return ' '.join ([ \
            ("#%i KNN%6i CId%6i " % (self.numPredictions, self.kNN, self.last_custId)), \
            ("[%s %s]" % (predDate, actualDate)), \
            ("[%6.2f %6.2f]" % (predSales,actualSales)), \
            ("[%s]"    % self.matchFlags[(dateMatch, salesMatch)]), \
            ("[%%D %s %%S %s ]"  % (self.pctString(self.dateMatches, self.numPredictions), \
                             self.pctString(self.salesMatches,self.numPredictions))), \
            ("[%%DS %s ]" % self.pctString(self.dateSalesMatches,self.numPredictions)),\
            ("#D/S/DS %i %i %i" % (self.dateMatches, self.salesMatches, self.dateSalesMatches)) \
        ])


def doTraining(nTrainSamples, nTestSamples, kNN_list, decaydays, dayknn, centerfunc, predfunc): 
    test  = readDataFileCache(FILE_TEST_CSV,  FILE_TEST_CACHE)
    train = readDataFileCache(FILE_TRAIN_CSV, FILE_TRAIN_CACHE)
    trainXVal, testXVal = makeCrossValidationData(train, nTrainSamples, nTestSamples)
    testXValAnswers = makeCrossValidationAnswers(testXVal)

    engine = NearestCustIdsEngine(testXVal, trainXVal, calcWeightRow(decaydays), \
                                  centerfunc, predfunc, dayknn=dayknn) 
    
    trackers = [PerformanceTracker(testXVal, testXValAnswers, engine, k) for k in kNN_list]
    for custId in sorted(testXVal.keys()):
        for tracker in trackers:
            print tracker.addPrediction(custId)
        print 
        sys.stdout.flush()


def parseCommandLine():
    parser = argparse.ArgumentParser("\nKNN for dunnhumbys Shopper Challenge on Kaggle.com\n")
    parser.add_argument('--knns', nargs='+', type=int, metavar='K', default=[7], 
                        help='List of number of nearest neighbors to use')
    parser.add_argument('--dayknn', action='store_true', 
                        help='Use KNN values to get K neigbors on the predicted date')
    parser.add_argument('--decaydays', type=int, help='Time decay constant for weights (in days)')
    parser.add_argument('--centerfunc', choices=['mean','median','geomean','rms'],  
                                       help='Function used in scaling up preditors')
    parser.add_argument('--predfunc',   choices=['mean','median','geomean','rms'],  
                                       help='Function used to reduce knns to prediction')
    parser.add_argument('--ntrain', type=int, help='Number of training set customers to sample')
    parser.add_argument('--ntest',  type=int, help='Number of test set customers so sample')

    parser.add_argument('--makesub', help='Submission file to write test set predictions to', metavar='FILE')
    parser.add_argument('--randseed',  type=int, help='Set a specific seed value for the random number generator')
    
    options = parser.parse_args()
    return options 

def echoOptions(cl):
    print "\n*** KNN for dunnhumbys Shopper Challenge on Kaggle.com ***\n"
    print "Parameters being used:"
    cl_vars = vars(cl)
    for cl_var in cl_vars:
        print cl_var,"=",cl_vars[cl_var]
    print 

def main():
    global RAND_SEED
    cl = parseCommandLine()
    echoOptions(cl)
    if cl.randseed:
        RAND_SEED = cl.randseed
    if cl.makesub:
        print "TEST SET GENERATION NOT IMPLEMENTED YET" # run through test set & write a submission 
    else: 
        str2func = { 'mean':numpy.mean, 'median':numpy.median, 'geomean':geometricMean, 'rms':RMS } 
        doTraining(cl.ntrain, cl.ntest, cl.knns, cl.decaydays, cl.dayknn, \
                   str2func[cl.centerfunc], str2func[cl.predfunc]  )
    # Done


def EARLY_TEST_CODE():
    test  = readDataFileCache(FILE_TEST_CSV,  FILE_TEST_CACHE)
    train = readDataFileCache(FILE_TRAIN_CSV, FILE_TRAIN_CACHE)

    print "Initializing lookup tables"
    sys.stdout.flush()
    nn_engine = NearestCustIdsEngine(test, train, calcWeightRow(30), numpy.mean, numpy.mean, dayknn=True) 
    # TODO try: numpy.mean, numpy.median, geometricMean, RMS 
    
    print "Computing distances"
    t0 = time.time()
    nearestNeighbors = nn_engine.calcNearestNeighbors(40, 5)
    print "Dist calculation time:", time.time()-t0
    for dist, cid in nearestNeighbors: 
        print "CustID:", cid, "Distance:", dist
    print
    sys.stdout.flush()

    t0 = time.time()
    nearestNeighbors = nn_engine.calcNearestNeighbors(40, 10)
    print "Dist calculation time:", time.time()-t0
    for dist, cid in nearestNeighbors: 
        print "CustID:", cid, "Distance:", dist
    print 
    sys.stdout.flush()

    t0 = time.time()
    nearestNeighbors = nn_engine.calcNearestNeighbors(123, 15)
    print "Dist calculation time:", time.time()-t0
    for dist, cid in nearestNeighbors: 
        print "CustID:", cid, "Distance:", dist
    print 
    sys.stdout.flush()

    # loop through test & make some predictions 
    KNN_TO_USE = 100
    NUM_TEST_CUSTIDS = 100
    testCustIds = sorted(test.keys())
    for testCustId in testCustIds[0:NUM_TEST_CUSTIDS]:
        t0 = time.time()
        pred = nn_engine.makePrediction(testCustId, KNN_TO_USE)
        print "\nPrediction:", pred
        print "Prediction calculation time:", time.time()-t0
        print "\n-----------------------------------------------------\n"
        sys.stdout.flush()
    
main()
# cProfile.run('main()')

# For command line, for optimization: 
# vary K, (process a set of K values per run, 1,2,4,...1024) 
# vary decayDays  (1,2,4,8...1024, 1000000)
# vary centering func for scaling (median, mean, geomean, RMS)
# vary prediction reduce func for predictions (median, mean, geomean, RMS)
# sample size for test & train
# compare K nearest neighbors from all days, vs k-nearest-neighbors on picked day --dayKNN --allKNN

# compare clipped predictors <10 then averaged, vs average predictor then clip <10

# for prediction, weight predictors by exp(MCC) (but for mean only? not median, geomean, RMS?)

# ADD SAMPLING
# 100$ sample -> 40 hrs
# 50% sample  -> 10 hrs
# 25% sample  -> 2.5 hours
# 10% sample  -> 25 minutes

# Weight cutoffs over time/date? 
# if wt < X, then wt = 0
# <0.1 -> 90% covered, <0.03 -> 97% covered, <0.01 -> 99% covered

# Scale by date?
# MRMR enhancement?

