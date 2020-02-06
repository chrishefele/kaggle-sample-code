import pandas
import csv

DOWNLOAD_DIR = '/home/chefele/kaggle/FlightQuest2/download/'
AIRPORT_FILE = DOWNLOAD_DIR + 'airports.csv'
TEST_FILE    = DOWNLOAD_DIR + 'testFlightsRev3.csv'

#DOWNLOAD_DIR = '/home/chefele/kaggle/FlightQuest2/download/OneDaySimulatorFiles/'
#TEST_FILE    = DOWNLOAD_DIR + 'test_20130704_1540_sample.csv'

""" 
testFlights.csv
===============
FlightHistoryId,CutoffTime,ArrivalAirport,ScheduledArrivalTime,CurrentLatitude,CurrentLongitude,CurrentAltitude,CurrentGroundSpeed,StandardPassengerCount,PremiumPassengerCount,FuelRemainingPounds,FuelCost,CrewDelayCost,OtherHourlyCosts,NonarrivalPenalty,DelayCostProportion30m,DelayCostProportion2h,MaxStandardDelayCost,MaxPremiumDelayCost
301897853,2013-07-05 21:56:51+00:00,KSEA,2013-07-05 16:30:00+00:00,41.230000,-112.629997,40000,436,12,113,16428.159722,1.90,614.09,1783.96,100000.00,0.293,0.357,35.91,90.65
"""

"""
airports.csv
============
airport_icao_code,latitude_degrees,longitude_degrees,altitude(feet)
KBOS,42.363,-71.006,20.0
KJFK,40.640,-73.779,14.0
"""

def testFlightsInfo_CPython(test_file=TEST_FILE):
    # iterates over rows of flight info (one row per test flight)
    test_flights = pandas.read_csv(test_file)
    airports     = pandas.read_csv(AIRPORT_FILE)
    renames = { 'airport_icao_code':'ArrivalAirport',   
                'latitude_degrees' :'ArrivalLatitude',
                'longitude_degrees':'ArrivalLongitude', 
                'altitude(feet)'   :'ArrivalAltitude' }
    airports = airports.rename(columns=renames).set_index('ArrivalAirport')
    flight_info = test_flights.join(airports, on='ArrivalAirport')
    nrows, ncols = flight_info.shape
    # NOTE .irow below will be deprecated in pandas >0.12.0, but I'm running 0.7.0 here
    return [ flight_info.irow(r) for r in xrange(nrows) ]

# -----------------------------------------------------------------
# The following block of code is equivilent to 
# testFlightsInfo_CPython(), but eliminates the dependence on Pandas, 
# so that it can be ported to IronPython/.NET (if necessary)
# -----------------------------------------------------------------

def airportInfo():
    # returns a dict where airport codes map to a dict of airport info
    with open(AIRPORT_FILE, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        airport_info = {}
        for row in csv_reader:
            airport_info[row['airport_icao_code']] = {
                    'ArrivalLatitude' : float(row['latitude_degrees' ]) ,
                    'ArrivalLongitude': float(row['longitude_degrees']) ,
                    'ArrivalAltitude' : float(row['altitude(feet)'   ])  }
        return airport_info

def autoCast(s):
    for fn in (int, float):
        try:
            return fn(s)
        except ValueError:
            pass
    return s

def autoCastDict(d):
    return { k:autoCast(d[k]) for k in d }

def testFlightsInfo_IronPython(test_file=TEST_FILE):
    # iterates over rows of flight info (one row per test flight)
    airport_info = airportInfo()
    test_flights_info = []
    with open(test_file, 'r') as csvfile:
        for flight_info in csv.DictReader(csvfile):
            arrival_airport = flight_info['ArrivalAirport']
            arrival_info = airport_info[arrival_airport]
            d = autoCastDict(dict(flight_info.items() + arrival_info.items()))
            test_flights_info.append(d)
    return test_flights_info # returns a list of { colName:value }, 1 dict per row

# -----------------------------------------------------------------

def testFlightsInfo(test_file=TEST_FILE):
    # pick a version, depending on environment
    return   testFlightsInfo_CPython(test_file)
    # return testFlightsInfo_IronPython(test_file=TEST_FILE)

# -----------------------------------------------------------------

def _do_test():
    tfi = testFlightsInfo()
    print "test flights read:", len(tfi)
    for f in tfi:
        print f
        # print [(k,f[k]) for k in sorted(f)]
        print '\nFUEL COST:', f['FuelCost'] # example of accessing a single value

if __name__ == '__main__':
    _do_test()

