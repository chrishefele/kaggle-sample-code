# nnpath_backbone.py
#
# Generates a nearest-neightbor path avoiding a 'backbone' path for the  
# "Traveling Santa Problem" problem Kaggle contest
#
# usage: python nnpath_backbone.py <backbone_infile> <backbone_column_tag> <subtour_length> s<tours_outfile>
# 

import pandas
import numpy as np
from itertools import izip
import sys

CITIES_FILE = '/home/chefele/kaggle/Santa/download/santa_cities.csv'
PRINT_MOD = 200  # print status update every N cities

MAX_CITIES      = 150000
MAX_REGION_SIZE =  40000  # >= the diagonal of the 20k x 20k region
REGION_SIZE     =   1000

# REGION_SIZE
# 
# The region size is tunable, and should be set with care. 
# When searching for nearest neightbors for the next node in a path,
# neighboring nodes that are more than REGION_SIZE away are
# all thrown out to save processing time.  The assumption is that
# 'obviously' something that far away could not be a nearest-neighbor. 
# So setting REGION_SIZE too HIGH results in extra computation. 
#
# On the other hand, setting it too LOW can result in extra computation, too.
# Rarely (~1% of the path) you actually do need do find a far-off neighbor 
# (i.e. near the end of the path, when most nodes already visited).
# In that case, when no suitable neighbor is found within REGION_SIZE,
# the code does a FULL search of ALL points (which is obviously much slower).
# 
# The optimum REGION_SIZE is somewhere 500 to 2000 with this dataset. 
# The nodes lie in a plane that's 20,000 x 20,000, so the surrounding region
# of a node corresponds to about 1/10th of each X or Y axis.
#

def reverse_tail(x,n):  # reverse last n elements of a list
    tail = x[-n:]
    tail.reverse()
    return x[:-n] + tail


class Tour:

    edges = [set() for _ in xrange(MAX_CITIES)]  # shared across all tour instance)
    tour_num = 0

    def __init__(self, cities_file=CITIES_FILE, start_city_id=0):
        self.start_city_id = start_city_id
        self.tour_city_ids = [start_city_id]

        Tour.tour_num += 1
        self.tour_num = Tour.tour_num

        self.cities = pandas.read_csv(cities_file)
        self.cities['visited'] = False
        self.cities['visited'][start_city_id] = True

    def edge_add(self, node1, node2):    
        Tour.edges[node1].add(node2)
        Tour.edges[node2].add(node1)

    def edge_remove(self, node1, node2): 
        Tour.edges[node1].remove(node2)
        Tour.edges[node2].remove(node1)
        
    def edge_exists(self, node1, node2): 
        return (node2 in Tour.edges[node1]) or (node1 in Tour.edges[node2])

    def preload_tour(self, city_id_list):
        start_city_id = city_id_list[0]
        self.start_city_id =  start_city_id
        self.tour_city_ids = [start_city_id]
        self.cities['visited'] = False
        self.cities['visited'][start_city_id] = True
        for cur_city_id, next_city_id in zip(city_id_list[:-1], city_id_list[1:]):
            self.edge_add(cur_city_id, next_city_id)
            self.tour_city_ids.append(next_city_id)
            self.cities['visited'][next_city_id] = True
        # add edge returning back to start node to complete the tour
        self.edge_add(city_id_list[0], city_id_list[-1]) 
        return       (city_id_list[0], city_id_list[-1]) 

    def next_edge(self, region_size=REGION_SIZE, update_path_set=set() ):  
        # calculate the next edge in the tour
        # first, find candidate cities (i.e. nearby & unvisited cities)
        cur_city_id = self.tour_city_ids[-1]
        dx = self.cities['x']-self.cities['x'][cur_city_id]
        dy = self.cities['y']-self.cities['y'][cur_city_id]
        self.cities['dist'] = np.sqrt(dx*dx+dy*dy)
        mask_inregion  = self.cities['dist'] < region_size
        mask_unvisited = np.logical_not( self.cities['visited'] )
        #mask_updatepath = self.cities['id'].map(lambda cid: cid in update_path_set)
        mask = np.logical_and( mask_inregion, mask_unvisited)
        #mask = np.logical_and( mask         , mask_updatepath)
        candidate_cities = self.cities[ mask ] 
        candidate_cities = candidate_cities.sort(['dist'])

        # loop through sorted candidate cities (closest to most distant) and 
        # pick a city that has no existing edge to the candidate city (if possible)
        # and that is in the update path 
        some_candidates  = False
        picked_city      = False
        for candidate_city_id in candidate_cities['id']: 
            if candidate_city_id not in update_path_set:
                continue
            some_candidates = True
            if not self.edge_exists(cur_city_id, candidate_city_id):
                picked_city = True
                self.edge_add(cur_city_id, candidate_city_id)
                self.tour_city_ids.append(candidate_city_id)
                self.cities['visited'][candidate_city_id] = True
                # print "\n", self.cities['dist'][candidate_city_id],"NNDIST" # TODO Remove this debug print
                break

        if some_candidates and picked_city: 
            # This is the usual case 
            return (cur_city_id, candidate_city_id) # new edge

        if some_candidates and not picked_city:
            # Borderline case: Must get to a city, because it's the only
            # remaining node, but can't get there becuase paths to it
            # were already used by one or both tours. 
            # Fix this by redoing this tour's most recent edge selections.
            # When it issue happens, it's usually on the final few edges
            self.fix_cant_get_there_from_here(candidate_city_id, cur_city_id)
            return self.next_edge(update_path_set=update_path_set)

        if not some_candidates:
            # Borderline case: No candidates because no nearby unvisited cities
            # within the regional area. The solution is to widen the region.
            print '\nDoing GLOBAL SEARCH at node:',cur_city_id,
            wide_region_next_edge = self.next_edge(region_size=MAX_REGION_SIZE, \
                                                   update_path_set=update_path_set)
            print  'Success! Found edge:', wide_region_next_edge
            return wide_region_next_edge

    def fix_cant_get_there_from_here(self, there, here):  
        # Fix this issue by reversing the last N cities in the current tour, picking the 
        # cut point to ensure the 2 new resulting edges don't already exist
        print 'Recent path:', self.tour_city_ids[-10:]
        print '\nNO free edge:', here, '->', there, 

        for n in xrange(2, len(self.tour_city_ids)-1):
            precut_city_id  = self.tour_city_ids[-n-1]
            postcut_city_id = self.tour_city_ids[-n ]
            cur_city_id     = self.tour_city_ids[-1]
            target_city_id  = there

            if not self.edge_exists(precut_city_id,  cur_city_id   ) and \
               not self.edge_exists(postcut_city_id, target_city_id):
                print 'but REVERSING last', n, 'cities fixed this.'
                self.tour_city_ids = reverse_tail(self.tour_city_ids, n)
                print 'Fixed  path:', self.tour_city_ids[-10:]
                # NOTE removed the edge_remove below so as to 'blacklist' this path 
                # sometimes reversing 2 cities leads to another dead-end & thus 
                # endless flipping of the last 2 cities 
                # self.edge_remove(precut_city_id,  postcut_city_id)
                self.edge_add(   precut_city_id,  cur_city_id)
                return
        raise RuntimeError('and REVERSING cities FAILED')

    def last_edge(self, update_path_set=set()):
        print '\nFinalizing last edge'
        # revise starting node status so we can return to it
        self.cities['visited'][self.start_city_id] = False  
        last_edge = self.next_edge(update_path_set=update_path_set)
        print 'Edge completing tour to starting city is:', last_edge
        self.tour_city_ids.pop() # ...since last edge is implied
        return last_edge 

    def tour_dist(self):  # total path length of the tour 
        dist = 0 
        for city1_id, city2_id in izip(self.tour_city_ids[:-1], self.tour_city_ids[1:]):
            dx = self.cities['x'][city1_id] - self.cities['x'][city2_id]
            dy = self.cities['y'][city1_id] - self.cities['y'][city2_id]
            dist += np.sqrt(dx*dx + dy*dy)
        return(dist)
    

def echo(x, tag): 
    print tag, x
    return x
        
def print_status(loop):
    if loop % PRINT_MOD == 0:
        print loop,
        sys.stdout.flush()

def chunks(l, n):
    # split a list into chunks of length n
    return [l[i:i+n] for i in range(0, len(l), n)]

def write_tours(tour1, tour2, outfile):
    fout = open(outfile, 'w')
    fout.write('path1,path2\n')
    for city1, city2 in izip(tour1, tour2):
        line_out = str(city1) + ',' + str(city2) + '\n'
        fout.write(line_out)
    fout.close()


def main():
    print "\n*** Nearest Neighbor Backbone Tour Avoidance (with Subtours) for Santa TSP ***\n"
    backbone_file   = echo(sys.argv[1],     'Tour 1 (backbone) file    :')
    backbone_tag    = echo(sys.argv[2],     'Tour 1 (backbone) col tag :')
    chunk_size      = echo(int(sys.argv[3]),'Subtour size              :')
    tours_outfile   = echo(sys.argv[4],     'Tours output file         :')

    tour1 = Tour()
    backbone_tour = list(pandas.read_csv(backbone_file)[backbone_tag])
    tour1.preload_tour(backbone_tour)
    tour1_start = tour2_start = tour1.start_city_id

    tour2 = Tour(start_city_id=tour1_start)

    # find a path through each subtour/chunk seperately
    node_last = tour1_start
    for chunk_num, update_chunk in enumerate(chunks(backbone_tour, chunk_size)):
        update_chunk_set = set( update_chunk + [node_last] )
        num_nodes = len(update_chunk_set)
        edges_needed = num_nodes - 1
        print '\n\nFinding',edges_needed,'edges for subtour#', chunk_num+1,'\n'
        for loop in range(edges_needed):
            print_status(loop)
            edge = tour2.next_edge(update_path_set=update_chunk_set)
            node_nexttolast, node_last = edge 

    # last edge returns to start, completing the tour
    update_chunk_set = set( update_chunk + [tour1_start] )
    tour2.last_edge(update_path_set=update_chunk_set) 

    print "\n\nRESULTS ",
    print "tour_1_dist:", int(tour1.tour_dist()), "tour_2_dist:", int(tour2.tour_dist()),
    print "max_dist:", int(max(tour1.tour_dist(), tour2.tour_dist())),
    print "start_city_1:", tour1_start, "start_city_2:", tour2_start
    print
    print "Writing tours to:", tours_outfile
    write_tours(tour1.tour_city_ids, tour2.tour_city_ids, tours_outfile)
    print "Done.\n"


if __name__ == '__main__':
    main()
