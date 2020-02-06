
# For each driver, randomly pick a set of 200 trips from the set of all 
# OTHER drivers' trips. Put symlinks to those selected trip files in 
# the "trips.other" directory.
#
# Also create symlinks to each drivers personal trips. 
# Those are put in a parallel "trips.self" directory. 
#
# Runtime ~ 4 minutes

import os, os.path, sys
import random
import shutil

SOURCE_DIR       = "../download/drivers"
OTHER_DRIVERS_DIR  = "../data/drivers_other"
SELF_DRIVERS_DIR   = "../data/drivers_self"
MAX_TRIP_ID      = 200

def clean_dir(adir):
    if os.path.exists(adir):
        shutil.rmtree(adir)
    os.makedirs(adir)

def main(): 

    driver_dirs = os.walk(SOURCE_DIR).next()[1]
    trip_files  = [str(trip_id)+'.csv' for trip_id in xrange(1, MAX_TRIP_ID+1)]

    for cur_driver_dir in sorted(driver_dirs):

        print cur_driver_dir, 
        sys.stdout.flush()

        clean_dir(SELF_DRIVERS_DIR  + '/' + cur_driver_dir)
        clean_dir(OTHER_DRIVERS_DIR + '/' + cur_driver_dir)
     
        for cur_trip_id in xrange(1, MAX_TRIP_ID+1):

            # destination link that we'll assign a random trip to 
            other_trip_symlink = OTHER_DRIVERS_DIR + '/' \
                                + cur_driver_dir + '/' + str(cur_trip_id) + '.csv'

            # pick a random trip file from a random directory of *other* drivers
            rand_driver_dir = random.choice(driver_dirs)
            while rand_driver_dir == cur_driver_dir:
                rand_driver_dir = random.choice(driver_dirs)
            rand_trip_file = os.path.abspath(SOURCE_DIR) + '/' \
                + rand_driver_dir + '/' + random.choice(trip_files)

            # create the symlink to the randomly chosen file (avoids copying)
            os.symlink(rand_trip_file, other_trip_symlink)

            # Next, for convenience, link original trip files in a parallel directory
            suffix = cur_driver_dir + '/' + str(cur_trip_id) + '.csv'
            source_trip_file    = os.path.abspath(SOURCE_DIR) + '/' + suffix
            self_trip_symlink   = SELF_DRIVERS_DIR              + '/' + suffix
            os.symlink(source_trip_file, self_trip_symlink)


if __name__ == '__main__':
    main()
