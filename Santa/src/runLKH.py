# runLKH.py
#
# Script to run the LKH traveling-salesman problem solver
# LKH requires files in a certain format, and this script
# creates these files temporarily & feeds them to LKH.
#
# usage: runLKH <cities_infile.csv> <subtour_infile.csv> <subtour_col_tag> 
#               <subtour_method>    <subtour_nodes>      <besttour_outfile.csv> 

import sys
import os
import pandas
import tempfile
from itertools import izip

LKH_EXECUTABLE = '/home/chefele/kaggle/Santa/LKH/LKH'
#LKH_EXECUTABLE = '/home/chefele/kaggle/Santa/src/mockLKH.sh'

def read_cities_csv(fname):
    # cities file has columns:  id, x, y
    print 'Now reading cities info from:', fname
    cities = pandas.read_csv(fname)
    print len(cities),'cities read, each with data:', list(cities.columns),'\n'
    return cities

def write_cities_tsp(cities, fname):
    # cities is a pandas dataframe with id, x, y of each city
    # this writes a .tsp format 
    print "Writing cities info to .TSP file:", fname,'\n'
    fout = open(fname,'w')
    cities['id'] += 1 #NOTE LKH needs non-zero city names

    header = '\n'.join([
        'NAME : santa_cities',
        'COMMENT : santa_cities',
        'TYPE : TSP',
        'DIMENSION : ' + str(len(cities)),
        'EDGE_WEIGHT_TYPE : EUC_2D',
        'NODE_COORD_SECTION'
    ])
    fout.write(header+'\n')
    for cid, cx, cy in izip(cities['id'], cities['x'], cities['y']):
        outline = ' '.join((str(cid), str(cx), str(cy)))
        fout.write(outline+'\n')
    fout.close()

def read_subtour_csv(fname, col_tag):
    # subtour file has 2 columns:  path1, path2
    print 'Reading subtour tour from:', fname,'\n'
    subtour = pandas.read_csv(fname)
    print len(subtour),'edges read, each with data:', list(subtour.columns)
    return subtour[col_tag]

def write_subtour_tsp(subtour_cities, fname):
    print "Writing subtour to .TSP file:", fname,'\n'
    fout = open(fname,'w')
    header = '\n'.join([ 'NAME : santa_subtour', 'TOUR_SECTION' ])
    fout.write(header+'\n')
    subtour_cities += 1 # NOTE: LKH needs 1-150000, not 0-149999
    for city in subtour_cities:
        outline = str(city) 
        fout.write(outline+'\n')
    fout.close()

def write_parameters_par(parameters_fname, cities_infile_tsp, 
                     subtour_infile_tsp, subtour_method, subtour_nodes, 
                     besttour_outfile_tsp):
    print "Writing LKH parameters to:", parameters_fname,'\n'
    fout = open(parameters_fname,'w')
    header = '\n'.join([
        'PROBLEM_FILE = ' + cities_infile_tsp, 
        'RUNS = 1',
        'TOUR_FILE = ' + besttour_outfile_tsp,
        'SUBPROBLEM_SIZE = ' + str(subtour_nodes) + ' ' + subtour_method + ' ' + 'BORDERS', 
        'SUBPROBLEM_TOUR_FILE = ' + subtour_infile_tsp, 
        '# INITIAL_TOUR_ALGORITHM = ',
        '# SEED = 1'
    ])
    fout.write(header+'\n')
    fout.close()

def call_LKH(parameter_file):
    cmd_line = ' '.join([LKH_EXECUTABLE, parameter_file])
    print "Calling LKH using command line:", cmd_line,'\n'
    sys.stdout.flush()
    os.system(cmd_line)
    print "\nReturned from LKH\n"
    sys.stdout.flush()

def read_besttour_tsp(fname):
    print 'Now reading best LKH tour file from:', fname,'\n'
    tour = []
    for line in open(fname):
        if line.strip().isdigit() and int(line.strip())!= -1:
            tour.append(int(line) - 1)  #NOTE: renumbers cities 0-149999
            if len(tour) == 1:
                print '< ...tour cities not displayed... >' 
        else:
            print line.strip()
    print len(tour), 'tour cities read'
    return tour

def write_besttour_csv(tour, besttour_outfile):
    print "Writing best tour file to:", besttour_outfile,'\n'
    fout = open(besttour_outfile, 'w')
    fout.write('path1,path2\n')
    for city in tour:
        outline = ','.join([str(city), str(city)])
        fout.write(outline + '\n')
    fout.close()

def echo_read(x,tag):
    print tag, x
    return x

def get_tempfile_name(prefix='tmp', suffix=''):
    tf = tempfile.NamedTemporaryFile(mode='w', prefix=prefix, suffix=suffix, delete=False)
    tf.close()
    return tf.name

def main():
    print '\n*** LKH Solver for Traveling Santa Problem ***\n'
    cities_infile_csv   = echo_read(sys.argv[1], 'Cities file        : ')
    subtour_infile_csv  = echo_read(sys.argv[2], 'Subtour file       : ')
    subtour_col_tag     = echo_read(sys.argv[3], 'Subtour column tag : ')
    subtour_method      = echo_read(sys.argv[4], 'Subtour algorithm  : ')
    subtour_nodes       = echo_read(sys.argv[5], 'Subtour nodes      : ')
    besttour_outfile_csv= echo_read(sys.argv[6], 'Best tour outfile  : ')
    print

    cities_tsp          = get_tempfile_name(prefix='santa-cities-',   suffix='.tsp')
    subtour_tsp         = get_tempfile_name(prefix='santa-subtour-',  suffix='.tsp')
    parameters_par      = get_tempfile_name(prefix='santa-params-',   suffix='.par')
    besttour_outfile_tsp= get_tempfile_name(prefix='santa-besttour-', suffix='.tsp')
    tempfiles = [cities_tsp, subtour_tsp, parameters_par, besttour_outfile_tsp]

    cities = read_cities_csv(cities_infile_csv)
    write_cities_tsp(cities, cities_tsp)

    subtour_cities = read_subtour_csv(subtour_infile_csv, subtour_col_tag)
    write_subtour_tsp(subtour_cities, subtour_tsp)

    write_parameters_par(parameters_par, cities_tsp, 
                     subtour_tsp, subtour_method, subtour_nodes, 
                     besttour_outfile_tsp)

    call_LKH(parameters_par)

    besttour = read_besttour_tsp(besttour_outfile_tsp)
    write_besttour_csv(besttour, besttour_outfile_csv)

    for tempfile in tempfiles:
        #os.remove(tempfile)
        pass

    print '\nDone.\n'


if __name__ == '__main__':
    main()


