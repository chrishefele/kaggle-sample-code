from main import *
from waypoints import FlightModel

def mainSubmission():

    """
    for zoneOptions 3333:
    opt,fval,zone,airspeedIntercept,airspeedSlope,ascentSlope,cruiseIntercept,cruiseSlope,descentSlope
    xopt,11527.95,3333,287.413149444,0.0176670380622,246.662015621,40783.9971869,-2.96301733324e-05,259.663105016
    """

    flightModelParameters = {  
            'airspeedSlope'     : 0.017667038062239245, 
            'cruiseIntercept'   : 40783.997186932749, 
            'ascentSlope'       : 246.6620156207245, 
            'airspeedIntercept' : 287.41314944402433, 
            'cruiseSlope'       : -2.9630173332396724e-05, 
            'descentSlope'      : 259.66310501643375 
    }
    flightModel = FlightModel(**flightModelParameters)
    zoneOptions = (3,3,3,3)
    npts_per_leg = NPTS_PER_LEG

    sub_file = 'submission.csv'

    #test_flights_info = testFlightsInfo(test_file=TEST_FILE_ONEDAY)
    test_flights_info = testFlightsInfo(test_file=TEST_FILE)

    print 'writing submission to:', sub_file
    write_submission(test_flights_info, flightModel, zoneOptions, npts_per_leg, sub_file)
    print 'done'

mainSubmission()

