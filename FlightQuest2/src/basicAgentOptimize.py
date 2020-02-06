from Simulator import Simulator
import pandas 
import numpy, scipy.optimize
import os, sys, time, itertools, copy
import basicAgent
from sklearn.cross_validation import KFold 
import numpy 
import pandas


SUBMISSION_DIR = "/home/chefele/kaggle/FlightQuest2/download/OneDaySimulatorFiles/"
SUBMISSION_FILE   = SUBMISSION_DIR + "sampleSubmissionBasicAgent.csv"
TEST_FLIGHTS_FILE = "/home/chefele/kaggle/FlightQuest2/download/OneDaySimulatorFiles/test_20130704_1540_sample.csv"

FINAL_SUBMISSION_FILE =  './sampleSubmissionBasicAgent.csv'
FINAL_TEST_FILE       =  '/home/chefele/kaggle/FlightQuest2/download/testFlightsRev3.csv'


initialFlightParams = {
    'cruise' : 35000,
    'speed'     : 450. ,
    'descend_distance': 150
}

flightParamsTemplate = { k:0 for k in initialFlightParams } 

def flightParamsToVector(flightParams):
    # convert from a dict of named flight parameters to an array of values (ordered by name)
    return numpy.array( [flightParams[param] for param in sorted(flightParams)] )

def vectorToFlightParams(flightVec, flightParamsTemplate):
    # convert an array of parameter values to a dict of named flight parameters 
    return { pname:pval for pname,pval in zip(sorted(flightParamsTemplate), flightVec) } 

class CostEngine:
    def __init__(self, flightParamsTemplate, submissionFile, testFlightsFile):
        self.submissionFile = submissionFile
        self.flightParamsTemplate = flightParamsTemplate
        self.testFlightsFile = testFlightsFile
        print "Starting simulator using:", testFlightsFile
        self.simulator = Simulator()
        print "Simulator started."

    def cost(self, flightParamsVector):
        # write submission waypoints (to submission_file)
        flightParams = vectorToFlightParams(flightParamsVector, self.flightParamsTemplate)
        basicAgent.make_basicAgent_submission(self.submissionFile, self.testFlightsFile, **flightParams)
        # calcuate cost using the simulator 
        submission_file_basename = os.path.basename(self.submissionFile)
        sim_cost = self.simulator.cost(submission_file_basename)
        # print time.asctime(), "currentCost:", sim_cost, "parameters:", flightParams
        return sim_cost

    def stop(self):
        self.simulator.stop()


def kfold_files(allTestFlightsFile, submission_dir, nfolds=3):
    df = pandas.read_csv(allTestFlightsFile)
    nrows, ncols = df.shape
    fnames = []
    for fold_num, (train_mask, test_mask) in enumerate(KFold(nrows, nfolds, indices=False)):
        fname_train = submission_dir + 'train-fold-{}.csv'.format(fold_num)
        fname_test  = submission_dir + 'test-fold-{}.csv'.format(fold_num)
        df[train_mask].to_csv(fname_train, index=False)
        df[ test_mask].to_csv(fname_test,  index=False)
        fnames.append( (fname_train, fname_test) ) 
        print 'writing cv train file:', fname_train
        print 'writing cv test  file:', fname_test
    return fnames 

def optimizer_callback(xk): 
    print time.asctime(), vectorToFlightParams(xk, initialFlightParams)

def print_results(fval, xopt):
    print
    print 'xopt,fval,zone,' + (','.join(k for k in sorted(initialFlightParams)))
    fltParams = vectorToFlightParams(xopt, initialFlightParams)
    fvalStr = str(fval)
    paramsStr = ','.join(str(fltParams[param]) for param in sorted(fltParams))
    print ','.join(['xopt',fvalStr, paramsStr])
    print fltParams
    print 

def filenameWithPid(f):
    # insert process id in filename to make it unique to a process
    # so that we can run multiple instances of this program in parallel
    f_dir  = os.path.dirname (f)
    f_name = os.path.basename(f)
    f_base, f_ext = os.path.splitext(f_name)
    f_pid = '-' + str(os.getpid())
    return f_dir + '/' + f_base + f_pid + f_ext 

def main():

    sub_file = SUBMISSION_FILE # sub_file = filenameWithPid(OPTIMIZER_SUB_FILE)
    costEngine = CostEngine(flightParamsTemplate, sub_file, TEST_FLIGHTS_FILE)
    x0 = flightParamsToVector(initialFlightParams)

    xopt, fval, iterations, fcalls, warnflag, allvecs = \
        scipy.optimize.fmin( costEngine.cost, x0, full_output=True, 
                             disp=False, retall=True,
                             callback=optimizer_callback ) 

    costEngine.stop()
    # os.remove(sub_file)

    print "\nFinal Optimized Parameters\n"
    print_results(fval, xopt)
    print "writing submission to:", FINAL_SUBMISSION_FILE
    flightParams = vectorToFlightParams(xopt, flightParamsTemplate)
    basicAgent.make_basicAgent_submission(FINAL_SUBMISSION_FILE, FINAL_TEST_FILE, **flightParams)
    print "Done."


def main_CV():

    sub_file_train = SUBMISSION_DIR + 'submissionCVTrain.csv'
    sub_file_test  = SUBMISSION_DIR + 'submissionCVTest.csv'
    x0 = flightParamsToVector(initialFlightParams)

    for fname_train, fname_test in kfold_files(TEST_FLIGHTS_FILE, SUBMISSION_DIR, nfolds=3):

        costEngineTrain= CostEngine(flightParamsTemplate, sub_file_train, fname_train)
        costEngineTest = CostEngine(flightParamsTemplate, sub_file_test , fname_test)

        xopt, fval, iterations, fcalls, warnflag, allvecs = \
            scipy.optimize.fmin( costEngineTrain.cost, x0, full_output=True, 
                                  disp=False, retall=True,
                                  callback=optimizer_callback ) 

        # now print CV scores
        print '\n*** CV scores ***\n'
        for k, xk in enumerate(allvecs):
            print 'k:',k, 
            print 'train_cost:', costEngineTrain.cost(xk),  
            print 'test_cost:',  costEngineTest.cost(xk), 
            print 'xk:', xk 

        print "stopping cost engines"
        costEngineTrain.stop()
        costEngineTest.stop()
        # os.remove(sub_file)

    print "Done"

def main_brute():
    sub_file_train = SUBMISSION_DIR + 'submissionBrute.csv'
    costEngine = CostEngine(flightParamsTemplate, sub_file_train, TEST_FLIGHTS_FILE)
    for cruise in numpy.linspace(10000, 50000, 40+1):
        for speed in numpy.linspace(150, 600, 45+1):
            for ddist in numpy.linspace(50, 300, 25+1):
                initialFlightParams = {'cruise':cruise, 'speed':speed, 'descend_distance':ddist}
                x0 = flightParamsToVector(initialFlightParams)
                print costEngine.cost(x0), initialFlightParams
    costEngine.stop()
    # os.remove(sub_file)
    print "Done"

if __name__=='__main__':
    main()
    # main_brute()
    # main_CV()  # NOTE uncomment this to use instead of main()

    # main_CV() does cross validation with the goal to
    # try to determine if the fmin() simplex algorithm overfits the parameters
    # However, after trying it, my conclusion is that the holdout set 
    # is minimized  at the same spot as the training set, i.e. not overfit. 



"""
FlightHistoryId                           301897853
CutoffTime                2013-07-05 21:56:51+00:00
ArrivalAirport                                 KSEA
ScheduledArrivalTime      2013-07-05 23:30:00+00:00
CurrentLatitude                               41.23
CurrentLongitude                            -112.63
CurrentAltitude                               40000
CurrentGroundSpeed                              436
StandardPassengerCount                          105
PremiumPassengerCount                            13
FuelRemainingPounds                        16428.16
FuelCost                                        1.9
CrewDelayCost                                614.09
OtherHourlyCosts                            1783.96
NonarrivalPenalty                            100000
DelayCostProportion30m                        0.293
DelayCostProportion2h                         0.357
MaxStandardDelayCost                          35.91
MaxPremiumDelayCost                           90.65
ArrivalLatitude                               47.45
ArrivalLongitude                           -122.312
ArrivalAltitude                                 433
"""
