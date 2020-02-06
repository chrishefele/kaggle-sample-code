import unzip2opt as u2
import numpy as np
import math 
import random
import sys
import time
import scipy.optimize

RANDOM_SEED = 1234567
random.seed(RANDOM_SEED)

def dist(node1, node2, nodes_x, nodes_y):
    dx = nodes_x[node1] - nodes_x[node2]
    dy = nodes_y[node1] - nodes_y[node2]
    edge_dist = math.sqrt(dx*dx + dy*dy)
    return edge_dist

def tour_length(tour_engine, nodes_x, nodes_y):
    # calculates tour length for moved cities (with displaced x/y coordinates
    # n1 = node, n2 = next_node[n1]
    return sum(( dist(n1,n2, nodes_x, nodes_y) for n1, n2 in enumerate(tour_engine.next_node)))

def main():

    print "\n*** Random City Movement for Traveling Santa Problem ***\n"

    # get tours through cities 
    tour_infile  = sys.argv[1] 
    print "Input tour file:", tour_infile, '\n'
    tour1_init, tour2_init = u2.read_tours(tour_infile) 
    assert len(tour1_init)==len(tour2_init)
    print 'Initializing tour engine...'
    tour1 = u2.TourEngine(tour1_init)
    tour2 = u2.TourEngine(tour2_init)

    # generate random displacements for each city, drawn from unit disk 
    N = len(tour1_init)
    radius = np.random.random(N)   # NOTE or try constant 1 radius? 
    radians= np.random.random(N)*2.0*np.pi
    unit_dx = np.sqrt(radius)*np.cos(radians)
    unit_dy = np.sqrt(radius)*np.sin(radians)

    # get nearest neighbor distance for each city in the tour
    print 'Calculating nearest-neightbor distances...'
    nn_dist = np.array( [float(nbr['dist'][0:1]) for nbr in tour1.neighbors] ) 
    print 'Example distances:', nn_dist[0:20],'\n'

    # add random displacements to city locations & show new tour lengths
    def moved_cities_tour_length(weight, tour):
        new_x = tour.nodes_x + (weight * unit_dx * nn_dist)
        new_y = tour.nodes_y + (weight * unit_dy * nn_dist)
        return tour_length(tour1, new_x, new_y)

    for weight in np.arange(-1.0, 1.0,0.02):
        print 'weight:', weight, 
        print 'tour1_len:', moved_cities_tour_length(weight, tour1)

    f = lambda w: pow(moved_cities_tour_length(w, tour1) - 6500000, 2)
    xopt, fval, ierr, numfunccalls = scipy.optimize.fminbound(f,0,1,full_output=True, disp=3) 



if __name__ == '__main__':
    main()

