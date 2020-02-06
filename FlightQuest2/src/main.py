import gcUtils 
from testFlightsInfo import testFlightsInfo
from waypoints import waypoints, FlightModel, oneWaypoint, concatWaypoints
from Simulator import Simulator
import pandas 
import numpy, scipy.optimize
import os, sys, time, itertools, copy

DOWNLOAD_DIR        = '/home/chefele/kaggle/FlightQuest2/download/'
TEST_FILE           = DOWNLOAD_DIR        + 'testFlightsRev3.csv'

DOWNLOAD_DIR_ONEDAY = '/home/chefele/kaggle/FlightQuest2/download/OneDaySimulatorFiles/'
TEST_FILE_ONEDAY    = DOWNLOAD_DIR_ONEDAY + 'test_20130704_1540_sample.csv'

OPTIMIZER_SUB_DIR  = DOWNLOAD_DIR_ONEDAY 
OPTIMIZER_SUB_FILE = OPTIMIZER_SUB_DIR + 'optimizerSubmission.csv'

NPTS_PER_LEG = 2  

ARRIVAL_ALTITUDE        = 17000   # feet 
ARRIVAL_RADIUS          = 65.1732 # in Nautical Miles, which is 75 statute miles 
ARRIVAL_RADIUS_SHRINKAGE= 0.99    # for smarterEndPosition 

def accumulateWaypoints(flight_id, flight_wpts, accumulator):
    # Concatenates current flight waypoints with previously accumulated waypoints.
    # Waypoint data stored as named 'columns' (i.e. dict mapping col_name->list).
    wpts = copy.copy(flight_wpts)
    lengths = [ len(wpts[col]) for col in wpts ]
    assert max(lengths) == min(lengths), 'waypoint object columns differ in length!'
    n_wpts = max(lengths)

    wpts['FlightId'] = (flight_id,) * n_wpts
    wpts['Ordinal' ] = range(1, n_wpts+1)
    if accumulator:
        assert len(accumulator) == len(wpts) # same number of columns
        for col in accumulator:
            accumulator[col].extend( wpts[col] )
    else:
        for col in wpts:
            accumulator[col] = list(wpts[col])

def smarterEndPosition(posn_begin, posn_end):
    # instead of targeting arrival airport, target a closer pt just inside the arrival area
    (lat_begin, lon_begin, alt_begin) = posn_begin
    (lat_end,   lon_end,   alt_end  ) = posn_end
    dist_begin_end  = gcUtils.gcDistNMile( (lat_begin,lon_begin), (lat_end,lon_end) )
    dist_end_smarterend = min(ARRIVAL_RADIUS, dist_begin_end) * ARRIVAL_RADIUS_SHRINKAGE
    lat_smarter, lon_smarter = gcUtils.gcPtAtDistance( 
                                (lat_end,lon_end), (lat_begin,lon_begin), 
                                dist_end_smarterend, gcUtils.EARTH_RADIUS_NM    )
    alt_smarter = ARRIVAL_ALTITUDE
    posn_smarterend = (lat_smarter, lon_smarter, alt_smarter)
    return posn_smarterend

def write_submission(test_flights_info, flightModel, zoneOptions, npts_per_leg, sub_file):
    wpts_accumulator = {}   # accumulates all waypoints for all flights
    for f in test_flights_info:
        flight_id  =    f['FlightHistoryId']
        posn_begin =   (f['CurrentLatitude'], f['CurrentLongitude'], f['CurrentAltitude'])
        posn_arrival = (f['ArrivalLatitude'], f['ArrivalLongitude'], f['ArrivalAltitude'])
        posn_end = smarterEndPosition(posn_begin, posn_arrival) # vs posn_end = posn_arrival
        flight_wpts = waypoints(posn_begin, posn_end, npts_per_leg, flightModel, zoneOptions)

        # now append the airport as  a final waypoint, following the 'smarter' end waypoint
        _, _, alt_arrival = posn_arrival
        airspeed_arrival = flightModel.airspeed(alt_arrival)
        airport_wpt = oneWaypoint(posn_arrival, airspeed_arrival)  
        flight_airport_wpts = concatWaypoints(flight_wpts, airport_wpt) 

        accumulateWaypoints(flight_id, flight_airport_wpts, wpts_accumulator)

    wpts_df = pandas.DataFrame(wpts_accumulator)
    col_order = ['FlightId','Ordinal','LatitudeDegrees',
                 'LongitudeDegrees','AltitudeFeet','AirspeedKnots']
    wpts_df.to_csv(sub_file, cols=col_order, index=False) 

def flightParamsToVector(flightParams):
    # convert from a dict of named flight parameters to an array of values (ordered by name)
    return numpy.array( [flightParams[param] for param in sorted(flightParams)] )

def vectorToFlightParams(flightVec, flightParamsTemplate):
    # convert an array of parameter values to a dict of named flight parameters 
    return { pname:pval for pname,pval in zip(sorted(flightParamsTemplate), flightVec) } 

class CostEngine:
    def __init__(self, test_flights_info, zoneOptions, npts_per_leg, flightParamsTemplate, submission_file):
        self.test_flights_info  = test_flights_info
        self.zoneOptions        = zoneOptions
        self.npts_per_leg       = npts_per_leg
        self.submission_file    = submission_file
        self.flightParamsTemplate = flightParamsTemplate
        print "Starting simulator..."
        self.simulator = Simulator()
        print "Simulator started."

    def cost(self, vecFlightParams):
        flightParams = vectorToFlightParams(vecFlightParams, self.flightParamsTemplate)
        flightModel  = FlightModel(**flightParams)  # waypoints.FlightModel
        write_submission( self.test_flights_info, flightModel, 
                          self.zoneOptions, self.npts_per_leg, self.submission_file )
        submission_file_basename = os.path.basename(self.submission_file)
        sim_cost = self.simulator.cost(submission_file_basename)
        print time.asctime(), "currentCost:", sim_cost, "zoneOptions:", self.zoneOptions
        return sim_cost

    def stop(self):
        self.simulator.stop()

initialFlightParams = {
    'ascentSlope'         : 18000./75.,   
    'descentSlope'        : 18000./75.,  
    'cruiseSlope'         : 0.,
    'cruiseIntercept'     : 35000.,
    'airspeedSlope'       : 200. / 10000.,
    'airspeedIntercept'   : 300. 
}

def optimizer_callback(xk): 
    print time.asctime(), vectorToFlightParams(xk, initialFlightParams)

def print_results(fval, zoneTuple, xopt):
    print
    print 'xopt,fval,zone,' + (','.join(k for k in sorted(initialFlightParams)))
    fltParams = vectorToFlightParams(xopt, initialFlightParams)
    fvalStr = str(fval)
    zoneStr =    ''.join(str(z)                for z     in zoneTuple)
    paramsStr = ','.join(str(fltParams[param]) for param in sorted(fltParams))
    print ','.join(['xopt',fvalStr, zoneStr, paramsStr])
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

    if len(sys.argv) != 3:
        print 'usage: python main.py [n for this process, 1<=n<=N] [N processes]'
        return # use (n,N) to run N instances in parallel 
    num_process   = int(sys.argv[1])
    num_processes = int(sys.argv[2])

    test_flights_info = testFlightsInfo(test_file=TEST_FILE_ONEDAY)
    x0 = flightParamsToVector(initialFlightParams)
    flightParamsTemplate = {k:0 for k in initialFlightParams}
    zoneOptions = (0,0,0,0)
    sub_file = filenameWithPid(OPTIMIZER_SUB_FILE)

    costEngine = CostEngine( test_flights_info, zoneOptions, NPTS_PER_LEG,
                             flightParamsTemplate, sub_file)

    for zoneOptions in itertools.product((3,2,1), repeat=4):
        if (hash(zoneOptions) % num_processes)+1  != num_process:
            continue # only examine a subset of the cases in this process

        costEngine.zoneOptions = zoneOptions
        xopt, fval, iterations, fcalls, warnflag = \
            scipy.optimize.fmin( costEngine.cost, x0, full_output=True, 
                                 disp=False, callback=optimizer_callback ) 
        print_results(fval, zoneOptions, xopt)

    costEngine.stop()
    os.remove(sub_file)


if __name__=='__main__':
    main()

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
