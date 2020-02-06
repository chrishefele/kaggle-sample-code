from __future__ import division
import csv
from itertools import chain
import pandas as pd
import basicAgentUtilities as u

#SUBMISSION_FILE   = "/home/chefele/kaggle/FlightQuest2/download/OneDaySimulatorFiles/sampleSubmissionBasicAgent.csv"
#TEST_FLIGHTS_FILE = "/home/chefele/kaggle/FlightQuest2/download/OneDaySimulatorFiles/test_20130704_1540_sample.csv"

def make_basicAgent_submission( sub_file, test_flights_file, 
                                cruise=None, descend_distance=None, speed=None):
    airports = u.read_airports()
    test_flights = u.read_flights_df(test_flights_file)
    waypoints = []
    waypoints = list(chain.from_iterable(
        u.direct_route_waypoints(
            row,
            airports[row["ArrivalAirport"]],
            cruise=cruise,
            descend_distance=descend_distance,
            speed=speed) for i, row in test_flights.iterrows()))
    # file_name = "%dk_cruise_%dmiles_descend_%dknots.csv" % (int(cruise/1000), descend_distance, speed)
    u.save_waypoints(sub_file, waypoints)


