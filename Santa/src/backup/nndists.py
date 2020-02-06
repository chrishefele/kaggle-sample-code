# nndists.py
# 
# Generates top N nearest-neightbor points for each point
# Part of the soln for the "Traveling Santa Problem" problem Kaggle contest
#
# usage: python nndists.py <cities_file> <outfile>

import pandas
import numpy as np
import sys
import cPickle

MAX_CITIES        = 150000
NEIGHBORS_NEEDED  = 100
DIST_THRESH_START = 512
PRINT_MOD         = 100  # print status update every N cities

# For best performance with the santa_cities.csv dataset, use: 
#   DIST_THRESH_START= 256 or more when NEIGHBORS_NEEDED= 100
#   DIST_THRESH_START=1024 or more when NEIGHBORS_NEEDED=1000

def calcDists(cities_file):

    dists = [None]* MAX_CITIES 
    # dists = list of dataframes, one per city. 
    # So dists[city_id] = city_dataframe, which 
    # has NEIGHBORS_NEEDED rows. 
    # Rows have city id 'id' & distance from city 'dist'.
    # Rows are sorted by 'dist' from city_id

    cities = pandas.read_csv(cities_file)

    for city_id in cities['id']:
        print_status(city_id)
        dx = cities['x']-cities['x'][city_id]
        dy = cities['y']-cities['y'][city_id]
        cities['dist'] = np.sqrt(dx*dx+dy*dy)

        dist_thresh = DIST_THRESH_START
        while True:
            nn_cities  =    cities[   cities['dist'] < dist_thresh ] 
            nn_cities  = nn_cities[nn_cities['dist'] > 0 ] 
            nrow, ncol = nn_cities.shape
            if nrow > NEIGHBORS_NEEDED:
                # print "city_id:", city_id, "dist_thresh:",dist_thresh,"nrows:",nrow
                break
            dist_thresh *= 2
        del nn_cities['x'] # to save space, only store 'id' & 'dist', not 'x' & 'y'
        del nn_cities['y']
        dists[city_id] = nn_cities[:NEIGHBORS_NEEDED].sort('dist') 
    return dists

def print_status(loop):
    if loop % PRINT_MOD == 0:
        print loop,
        sys.stdout.flush()

def write_distances(dists, outfile):
    print "\nWriting distances to:", outfile
    fout = open(outfile, 'wb')
    cPickle.dump(dists, fout)
    fout.close()

def main():
    print "\n*** Nearest Neighbor Distance Calculation for Santa TSP ***\n"
    cities_file = sys.argv[1]
    dists_file  = sys.argv[2]
    print "Input cities file    :  ", cities_file
    print "Output distances file:  ", dists_file
    print
    dists = calcDists(cities_file)
    write_distances(dists, dists_file)
    print "Done."

    print "\n=== Sample Data below ==="
    for ix, df in enumerate(dists[:10]):
        print "city_id:", ix
        print df[:10]
        print

if __name__ == '__main__':
    main()
