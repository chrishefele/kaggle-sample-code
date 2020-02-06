from itertools import izip
import cPickle
import math
import numpy
import random
import sys
import pandas
import itertools
import time

CITIES_NEIGHBORS_FILE = '/home/chefele/kaggle/Santa/data/santa_cities_nndists.pkl'
CITIES_INFO_FILE      = '/home/chefele/kaggle/Santa/download/santa_cities.csv'

MIN_PASS_IMPROVEMENT = 1000  # 1000 gets ~99% of possible improvement with this data
FAST_SEARCH = True

BATCH_SIZE = 1000  # Num nodes to process between prints of status updates

RANDOM_SEED = 1234567
random.seed(RANDOM_SEED)


class TourEngine:

    neighbors   = []    # read only, node nearest neighbors' info: id,dist
    nodes       = []    # dataframe of node id,x,y
    edges       = set() # *** read/write, set of all edges in all graphs/tours

    def __init__(self, starting_tour):

        # read only; starting tour of nodes
        self.starting_tour = starting_tour 

        # *** read/write; pointers to next node in this tour's path
        # that is, next_node[node_id] = next_node_id
        self.next_node = self.to_next_node_list(starting_tour)  

        # add all edges in the starting tour to the common edges set
        for node in xrange(len(self.next_node)):
            self.edge_add(node, self.next_node[node])

        if len(TourEngine.neighbors) == 0:
            TourEngine.neighbors = self.get_neighbors() 

        if len(TourEngine.nodes) == 0:
            TourEngine.nodes = self.get_nodes()  
        # for speed, convert to numpy arrays (pandas dataframe access much slower)
        self.nodes_x = numpy.array(TourEngine.nodes['x'])
        self.nodes_y = numpy.array(TourEngine.nodes['y'])

    def get_neighbors(self):
        print "Loading nearest neighbor distances from:", CITIES_NEIGHBORS_FILE,"...",
        sys.stdout.flush()
        fin = open(CITIES_NEIGHBORS_FILE, 'rb')
        neighbors = cPickle.load(fin)
        fin.close()
        print "Done."
        sys.stdout.flush()
        return neighbors # list of dataframes, one per city

    def get_nodes(self):
        print "Loading node data from:", CITIES_INFO_FILE,"...",
        sys.stdout.flush()
        nodes = pandas.read_csv(CITIES_INFO_FILE)
        print "Done."
        sys.stdout.flush()
        return nodes

    def to_next_node_list(self, node_lst):  # node list -> next_node_list
        assert len(node_lst) == len(set(node_lst)), 'Duplicate nodes!'
        assert len(node_lst) == max(node_lst)+1,    'Missing nodes!'
        next_node_lst = [None] * (max(node_lst)+1)
        # link the nodes in the body of the list 
        for cur_node, next_node in izip(node_lst[:-1], node_lst[1:]):
            next_node_lst[cur_node] = next_node
        # now link the end of the list to the start
        cur_node, next_node = node_lst[-1], node_lst[0]
        next_node_lst[cur_node] = next_node
        return next_node_lst

    def to_node_list(self, next_node_list, node_start):
        node_list = [node_start]
        node = next_node_list[node_start]
        while node != node_start:
            node_list.append(node)
            node = next_node_list[node]
        return node_list

    def get_current_tour_node_list(self):
        return self.to_node_list(self.next_node, self.starting_tour[0])
 
    def dist(self, node1, node2):
        dx = self.nodes_x[node1] - self.nodes_x[node2] 
        dy = self.nodes_y[node1] - self.nodes_y[node2] 
        edge_dist = math.sqrt(dx*dx + dy*dy)
        return edge_dist

    def edge_exists(self, node1, node2):
        return (node1,node2) in TourEngine.edges or (node2,node1) in TourEngine.edges       

    def edge_add(self, node1, node2):
        TourEngine.edges.add( (node1,node2) )
        TourEngine.edges.add( (node2,node1) )

    def edge_delete(self, node1, node2):
        TourEngine.edges.remove( (node1, node2) )
        TourEngine.edges.remove( (node2, node1) )
        
    def tour_update_generator(self):
        st = self.starting_tour
        # infinite sequence of nodes in random order to update
        node_generator = itertools.cycle(random.sample(st, len(st))) 

        for node1 in node_generator:  
            node2 = self.next_node[node1]
            assert node1 != node2
            dist12 = self.dist(node1, node2) # original edge

            swap_found = False
            best_dist_diff = 0

            for node3 in TourEngine.neighbors[node1].id:  # sorted by distance
                node4 = self.next_node[node3]
                if len(set((node1,node2,node3,node4)))<4: # skip overlaps
                    continue
                dist34 = self.dist(node3, node4) # original edge
                dist13 = self.dist(node1, node3) # proposed swap edge
                dist24 = self.dist(node2, node4) # proposed swap edge

                if (dist13 > dist12) and FAST_SEARCH:  # Much faster (3x-10x), but path length is ~1% more 
                    break  
                # note the symmetry of test, since the outer node2 loop will 
                # eventually hit the other points

                dist_diff = (dist13 + dist24) - (dist12 + dist34) 
                if dist_diff < best_dist_diff    and \
                   not self.edge_exists(node1, node3) and \
                   not self.edge_exists(node2, node4): 
                    swap_found = True
                    best_dist_diff, best_node3, best_node4 = dist_diff, node3, node4

            if swap_found:
                self.do_swap(node1, node2, best_node3, best_node4)
                self.edge_delete(node1, node2)
                self.edge_delete(best_node3, best_node4)
                self.edge_add(node1, best_node3)
                self.edge_add(node2, best_node4)

            yield True # NOTE this functionis a generator!

    def do_swap(self, node1, node2, node3, node4):
        # does a swap, updating self.next_node array in-place
        assert node2 == self.next_node[node1], 'node2 does not follow node1 in tour'
        assert node4 == self.next_node[node3], 'node4 does not follow node3 in tour'
        self.next_node[node1] = node3 
        self.reverse_path(node2, node4)
        self.next_node[node2] = node4 

    def reverse_path(self, head, tail):
        # reverses a path in self.next_node array in-place (like reversing a linked list)
        previous = None
        node = head 
        while node != tail:
            temp = self.next_node[node]
            self.next_node[node] = previous
            previous = node
            node = temp

    def get_current_tour(self):
        return self.to_node_list(self.next_node, self.starting_tour[0])

    def get_tour_length(self):
        # n1 = node, n2 = next_node[n1]
        return sum(( self.dist(n1,n2) for n1, n2 in enumerate(self.next_node)))


def read_tours(tour_file):
    df = pandas.read_csv(tour_file)
    tour1, tour2 = list(df['path1']), list(df['path2'])
    return (tour1, tour2)

def write_tours(tour1, tour2, outfile):
    fout = open(outfile, 'w')
    fout.write('path1,path2\n')
    lines = [str(n1)+','+str(n2) for n1, n2 in izip(tour1, tour2)]
    for line in lines:
        fout.write(line+'\n')
    fout.close()
    print '\nWrote 2-OPT tours to: ', outfile, '\n'


def main():

    print "\n*** 2-OPT for Traveling Santa Problem ***\n"

    tour_infile  = sys.argv[1] 
    tour_outfile = sys.argv[2] 
    print "Input  tour file:", tour_infile
    print "Output tour file:", tour_outfile
    print
    
    tour1_init, tour2_init = read_tours(tour_infile) 
    tour1 = TourEngine(tour1_init)
    tour2 = TourEngine(tour2_init)
    updater = itertools.izip(tour1.tour_update_generator(), tour2.tour_update_generator())

    print
    lmax_last = int(max(tour1.get_tour_length(), tour2.get_tour_length()))
    t0 = time.time()
    nodes_processed = 0
    pass_improvement = { 0:MIN_PASS_IMPROVEMENT }
    num_nodes = max(len(tour1_init),len(tour2_init))
    IMPROVING = True

    while IMPROVING:

        for _ in xrange(BATCH_SIZE):
            updater.next()
            nodes_processed += 1

        l1 = int(tour1.get_tour_length())
        l2 = int(tour2.get_tour_length())
        lmax = max(l1,l2)
        improvement = lmax_last - lmax
        lmax_last = lmax

        pass_num = int(nodes_processed / num_nodes) + 1
        if pass_num not in pass_improvement:
            # started a new pass...
            pass_improvement[pass_num] = 0
            if pass_improvement[pass_num - 1] < MIN_PASS_IMPROVEMENT:
                IMPROVING = False
        pass_improvement[pass_num] += improvement

        print "pass:", pass_num, "nodes:", nodes_processed, 
        print "tour1:", l1, "tour2:",l2,
        print "max:",lmax, "imp:",improvement, 
        print "pass_imp:", pass_improvement[pass_num],
        print "secs:", int(time.time()-t0)
        sys.stdout.flush()

        #print "checking tour lengths"
        #tour1_nodelist  = tour1.get_current_tour_node_list()
        #tour2_nodelist  = tour2.get_current_tour_node_list()
        #print "tour1_length", len(tour1_nodelist), 'uniq:',len(set(tour1_nodelist)),
        #print "tour2_length", len(tour2_nodelist), 'uniq:',len(set(tour2_nodelist))

    print "\nRESULTS ", 
    print "passes:", pass_num, " nodes:", nodes_processed, 
    print " tour1:", l1, " tour2:",l2,
    print " max:",lmax, " secs:", int(time.time()-t0)

    tour1_nodelist  = tour1.get_current_tour_node_list()
    tour2_nodelist  = tour2.get_current_tour_node_list()
    write_tours(tour1_nodelist, tour2_nodelist, tour_outfile)

    print "Done.\n"


def TEST_do_swap():
    l = [0,4,7,8,9,1,2,3,5,6]
    print "node list                 :", l 
    nnl = to_next_node_list(l)
    print "next node list before swap:", nnl
    do_swap(nnl, 2,3,7,8)
    print "next node list after  swap:", nnl
    print 
    print "node list                 :", l 
    print "node list after swap      :", to_node_list(nnl, 0)

if __name__ == '__main__':
    main()


