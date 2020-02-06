import unzip2opt as u2
import numpy as np
import math 
import random
import sys
import time
import scipy.optimize

RANDOM_SEED = 1234567
np.random.seed(seed=RANDOM_SEED)

NN_ESTIMATOR_PTS = 4  # 1-25 points OK (norm. radius 1-5)

MAX_WT = 2.0    # max weight for optimum weight search (+/-)
TABLE_ROWS = 20 # rows to print in table of len vs weight


def dist(node1, node2, nodes_x, nodes_y):
    dx = nodes_x[node1] - nodes_x[node2]
    dy = nodes_y[node1] - nodes_y[node2]
    edge_dist = math.sqrt(dx*dx + dy*dy)
    return edge_dist

def tour_length(tour_engine, nodes_x, nodes_y):
    # calculates tour length for moved cities (with displaced x/y coordinates
    # n1 = node, n2 = next_node[n1]
    return sum(( dist(n1,n2, nodes_x, nodes_y) for n1, n2 in enumerate(tour_engine.next_node)))

def moved_cities_xy(tour_engine, weight, unit_dx, unit_dy, nn_dist):
    new_x = np.rint( tour_engine.nodes_x + (weight * unit_dx * nn_dist) )
    new_y = np.rint( tour_engine.nodes_y + (weight * unit_dy * nn_dist) )
    return new_x.astype(int), new_y.astype(int)
 
def moved_cities_tour_length(weight, tour_engine, unit_dx, unit_dy, nn_dist):
    new_x, new_y = moved_cities_xy(tour_engine, weight, unit_dx, unit_dy, nn_dist)
    return tour_length( tour_engine, new_x, new_y )   

def random_disk(tour_init):
    # generate random displacements for each city, drawn from unit disk 
    N = len(tour_init)
    radius = 1.0 # np.random.random(N)   # NOTE or try constant 1 radius? random ring 
    radians= np.random.random(N)*2.0*np.pi
    unit_dx = np.sqrt(radius)*np.cos(radians)
    unit_dy = np.sqrt(radius)*np.sin(radians)
    return unit_dx, unit_dy

def get_nn_dist(tour_engine):
    # get nearest neighbor distance for each city in the tour
    print 'Calculating nearest-neightbor distances...'
    sys.stdout.flush()
    n = NN_ESTIMATOR_PTS 
    nbrs = tour_engine.neighbors
    nn_dist = np.array( [float(nbr['dist'][n-1:n])/math.sqrt(n) for nbr in nbrs] ) 
    # print 'Example distances:', nn_dist[0:3],'\n'
    return nn_dist

def make_table(wt_start, wt_end, wt_inc, f_vs_wt):
    # make tour length vs weight table
    print
    for weight in np.arange(wt_start, wt_end, wt_inc):
        print 'weight:', round(weight,4), 
        print 'tour_length:', f_vs_wt(weight)
        sys.stdout.flush()

def write_moved_cities(fname, xs, ys):
    fout = open(fname,'w')
    fout.write('id,x,y\n')
    for city_id, (x,y) in enumerate(zip(xs, ys)):
        outstring = ','.join([str(city_id), str(x), str(y)])
        fout.write(outstring + '\n')
    fout.close()
    print '\nwrote (id,x,y) of moved cities to: ', fname,'\n'
    sys.stdout.flush()

def write_opt_moved_cities(err_tourlen_w, w_lo, w_hi, 
                           tour, unit_dx, unit_dy, nn_dist, cities_outfile):
    wt_opt, fval, ierr, numfunccalls = \
        scipy.optimize.fminbound( err_tourlen_w, w_lo, w_hi, full_output=True, disp=3) 
    print "optimal weight:", wt_opt, 
    print "resulting length:", 
    print moved_cities_tour_length(wt_opt, tour, unit_dx, unit_dy, nn_dist)
    xs, ys = moved_cities_xy(tour, wt_opt, unit_dx, unit_dy, nn_dist)
    write_moved_cities(cities_outfile, xs, ys)

def pick_tour_init(tour_col_tag, tour1_init, tour2_init):
    if  tour_col_tag == 'path1':
        tour_init = tour1_init
    elif tour_col_tag == 'path2':
        tour_init = tour2_init
    else:
        raise RuntimeError, "ERROR: tour column tag must be 'path1' or 'path2' "
    return tour_init

def echo_set(x, tag):
    print tag,x
    return x

def main():
    print "\n*** Random City Movement for Traveling Santa Problem ***\n"
    tour_infile     = echo_set(sys.argv[1],     'input tour file       :')
    tour_col_tag    = echo_set(sys.argv[2],     'input tour column tag :')
    tour_len_target = echo_set(int(sys.argv[3]),'target tour length    :')
    cities_outfile1 = echo_set(sys.argv[4],     'output cities file 1  :')
    cities_outfile2 = echo_set(sys.argv[5],     'output cities file 2  :')
    print
    sys.stdout.flush()

    # get the tours through the cities 
    tour1_init, tour2_init = u2.read_tours(tour_infile) 
    tour_init = pick_tour_init(tour_col_tag, tour1_init, tour2_init)
    tour = u2.TourEngine(tour_init)

    tour_len_start = tour.get_tour_length()
    print 'Starting tour length:', tour_len_start
    if tour_len_start > tour_len_target:
        raise RuntimeError, "Target tour length is better than original tour length!"  

    nn_dist = get_nn_dist(tour) # nearest city distance estimate for each city
    unit_dx, unit_dy = random_disk(tour_init) # random displacement from unit disk 

    f_tourlen_w   = lambda wt: moved_cities_tour_length(wt, tour, unit_dx, unit_dy, nn_dist) 
    err_tourlen_w = lambda wt: pow(f_tourlen_w(wt) - tour_len_target, 2)

    make_table(-MAX_WT, MAX_WT, 1.0*MAX_WT/TABLE_ROWS, f_tourlen_w)

    write_opt_moved_cities(err_tourlen_w,  0, MAX_WT, 
                           tour, unit_dx, unit_dy, nn_dist, cities_outfile1)

    write_opt_moved_cities(err_tourlen_w, -MAX_WT, 0, 
                           tour, unit_dx, unit_dy, nn_dist, cities_outfile2)

    print 'Done.'


if __name__ == '__main__':
    main()

