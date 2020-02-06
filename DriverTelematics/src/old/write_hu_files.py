import os, os.path
import pandas
import numpy
import time
from linkSelfOtherTripFiles import clean_dir
from tripUtils import readTripFiles, tripInterpolate, tripHuMoments

DRIVERS_DIR     = "../download/drivers"
DATA_DIR        = "../data/drivers"

def write_hu_files(drivers_dir=DRIVERS_DIR):

    # for driver_dir in sorted(os.listdir(drivers_dir)):
    for driver_dir in list(sorted(os.listdir(drivers_dir)))[:10]: # NOTE for testing only 

        print "processing driver:", driver_dir

        full_driver_dir = drivers_dir + '/' + driver_dir
        trips = readTripFiles(full_driver_dir)

        statsfile = DATA_DIR + '/'  + 'hu'    + '/' + driver_dir + '.csv'
        f_statsfile = open(statsfile, 'w')
        f_statsfile.write('driver,trip,hu1,hu2,hu3,hu4,hu5,hu6,hu7\n')

        for trip_id, trip in trips.items():

            trip_interp = tripInterpolate(trip, 20)
            hu_moments =  tripHuMoments(trip_interp)

            f_statsfile.write(driver_dir + ',' + str(trip_id) + ',')
            f_statsfile.write(','.join([str(hu_moment) for hu_moment in hu_moments]))
            f_statsfile.write('\n')

            print full_driver_dir, "trip:", trip_id

        f_statsfile.close()

if __name__ == '__main__':
    write_hu_files()


