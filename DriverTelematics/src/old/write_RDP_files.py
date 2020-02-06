import os, os.path
import pandas
import numpy
from RDP import rdp, pldists, turnangles
import time
from linkSelfOtherTripFiles import clean_dir
from tripUtils import readTripFiles, writeTripFile, tripLegLengths, tripTurnAngles
import nltk

DRIVERS_DIR     = "../download/drivers"
DATA_DIR        = "../data/drivers"

RDP_DIST  = 10 # distance in meters (min about 5 to 10)
RDP_ANGLE = 30 # min turn angle in degrees  # TODO make >0 


def write_RDP_files(drivers_dir=DRIVERS_DIR):

    # for driver_dir in sorted(os.listdir(drivers_dir)):
    for driver_dir in list(sorted(os.listdir(drivers_dir)))[:10]: # NOTE for testing only 

        print "processing driver:", driver_dir

        full_driver_dir = drivers_dir + '/' + driver_dir
        trips = readTripFiles(full_driver_dir)

        dest_driver_dir = DATA_DIR + '/' + 'trips.rdp' + '/' + driver_dir
        clean_dir(dest_driver_dir)

        statsfile = DATA_DIR + '/'  + 'dists.angles'    + '/' + driver_dir + '.csv'
        f_statsfile = open(statsfile, 'w')
        f_statsfile.write('driver,trip,dist0,dist1,angle0,angle1\n')

        for trip_id, trip in trips.items():

            trip_dist    = rdp(trip,      epsilon=RDP_DIST,  dists_func=pldists)
            trip_ang     = rdp(trip,      epsilon=RDP_ANGLE, dists_func=turnangles)
            trip_distang = rdp(trip_dist, epsilon=RDP_ANGLE, dists_func=turnangles)

            fn = lambda tag: dest_driver_dir + '/' + str(trip_id) + '.' + tag + '.csv'
            writeTripFile(trip ,        fn('rdp.none'))
            writeTripFile(trip_dist,    fn('rdp.dist'))
            writeTripFile(trip_ang,     fn('rdp.angle'))
            writeTripFile(trip_distang, fn('rdp.distangle'))

            writeDriverStats(f_statsfile, driver_dir, trip_id, trip_distang)

            print full_driver_dir, "trip:", trip_id, 
            print trip.shape,"->", trip_distang.shape
            #rows_before, _ = trip.shape 
            #rows_after,  _ = trip_distang.shape 
            #print "reduction_factor=", round(float(rows_before)/rows_after)

        f_statsfile.close()


def writeDriverStats(fname, driver_id, trip_id, M):
    dists  =  nltk.ngrams( tripLegLengths(M)[:-1], 2)
    angles =  nltk.ngrams( tripTurnAngles(M),      2)
    for (dist0, dist1), (angle0, angle1) in zip(dists, angles):
        fname.write(','.join([str(driver_id), str(trip_id), str(dist0), str(dist1), str(angle0), str(angle1)]))
        fname.write('\n')
    

if __name__ == '__main__':
    write_RDP_files()


