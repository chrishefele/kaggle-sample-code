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

MIN_PASS_IMPROVEMENT_FULLTOUR = 1000  # must be >0; 1000 gets ~99% of possible improvement with this data
MIN_PASS_IMPROVEMENT_SUBTOUR  =   50  

FAST_SEARCH = True

BATCH_SIZE_FULLTOUR  = 1000  # Num nodes to process between prints of status updates
BATCH_SIZE_SUBTOUR   = 1000  # Num nodes to process between prints of status updates
MAX_DISTANCE         = 40000 # 20K x 20K image, so need any value >sqrt(2)*20K

RANDOM_SEED = 1234567
random.seed(RANDOM_SEED)


class TourEngine:

    neighbors   = []    # read only, node nearest neighbors' info: id,dist
    nodes       = []    # dataframe of node id,x,y
    edges       = {}    # read/write, dict of counts of all edges in all graphs/tours

    # edges is read/write, hash table of counts of all edges in all graphs/tours
    # edges = numpy.zeros(EDGE_HASH_TABLE_SIZE, int) 

    def __init__(self, starting_tour, load_neighbors=True):

        # read only; starting tour of nodes
        self.starting_tour = starting_tour 

        # *** read/write; pointers to next node in this tour's path
        # that is, next_node[node_id] = next_node_id
        self.next_node = self.to_next_node_list(starting_tour)  

        # add all edges in the starting tour to the common edges set
        for node in xrange(len(self.next_node)):
            self.edge_add(node, self.next_node[node])

        if len(TourEngine.neighbors) == 0 and load_neighbors:
            TourEngine.neighbors = self.get_neighbors() 

        if len(TourEngine.nodes) == 0:
            TourEngine.nodes = self.get_nodes()  
        # for speed, convert to numpy arrays (pandas dataframe access much slower)
        self.nodes_x = numpy.array(TourEngine.nodes['x'])
        self.nodes_y = numpy.array(TourEngine.nodes['y'])

    def clear_all_edges(self):
        TourEngine.edges = {}

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
        # NOTE asserts below doesn't work with subpaths (only with all nodes)
        # assert len(node_lst) == len(set(node_lst)), 'Duplicate nodes!'
        # assert len(node_lst) == max(node_lst)+1,    'Missing nodes!'
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

    def edge_hash(self, node1, node2):
        return hash( ( min(node1,node2), max(node1,node2) ) ) % EDGE_HASH_TABLE_SIZE

    def edge_exists(self, node1, node2):
        # return TourEngine.edges[self.edge_hash(node1,node2)] > 0
        return  (node1,node2) in TourEngine.edges or \
                (node2,node1) in TourEngine.edges       

    def edge_multiple_exists(self, node1, node2):
        # return TourEngine.edges[self.edge_hash(node1,node2)] > 1
        return  TourEngine.edges.get((node1,node2), 0) > 1 or \
                TourEngine.edges.get((node2,node1), 0) > 1

    def edge_add(self, node1, node2):
        # TourEngine.edges[self.edge_hash(node1,node2)] += 1
        e12 = (node1,node2)
        e21 = (node2,node1)
        TourEngine.edges[e12] = TourEngine.edges.setdefault(e12, 0) + 1
        TourEngine.edges[e21] = TourEngine.edges.setdefault(e21, 0) + 1

    def edge_delete(self, node1, node2):
        # TourEngine.edges[self.edge_hash(node1,node2)] -= 1
        e12 = (node1,node2)
        e21 = (node2,node1)
        edges = TourEngine.edges
        assert edges[e12]>0 and edges[e21]>0, "Deleting nonexistant edge"
        edges[e12] -= 1
        edges[e21] -= 1
        if edges[e12] == 0:
            del edges[e12]
        if edges[e21] == 0:
            del edges[e21]
        # TourEngine.edges.remove( (node1, node2) )
        # TourEngine.edges.remove( (node2, node1) )

    def tour_update_generator(self, update_path=None):
        if update_path == None:
            update_path = self.starting_tour
        update_path_nodes = set(update_path)

        # infinite sequence of nodes in random order to update
        node_generator = itertools.cycle(random.sample(update_path, len(update_path))) 
        for node1 in node_generator:  
            node2 = self.next_node[node1]
            assert node1 != node2
            dist12 = self.dist(node1, node2) # original edge

            swap_found = False
            if self.edge_multiple_exists(node1, node2):
                best_dist_diff = MAX_DISTANCE  # forces a swap
            else:
                best_dist_diff = 0 # only swaps if tot dist improves

            for node3 in TourEngine.neighbors[node1].id:  # sorted by distance
                node4 = self.next_node[node3]

                if len(set((node1,node2,node3,node4)))<4: # skip overlaps
                    continue
                if (node1 not in update_path_nodes) or (node2 not in update_path_nodes) or \
                   (node3 not in update_path_nodes) or (node4 not in update_path_nodes):
                    continue # only do 'in-region' updates along update path

                dist34 = self.dist(node3, node4) # original edge
                dist13 = self.dist(node1, node3) # proposed swap edge
                dist24 = self.dist(node2, node4) # proposed swap edge

                dist_diff = (dist13 + dist24) - (dist12 + dist34) 
                if dist_diff < best_dist_diff    and \
                   not self.edge_exists(node1, node3) and \
                   not self.edge_exists(node2, node4): 
                    swap_found = True
                    best_dist_diff, best_node3, best_node4 = dist_diff, node3, node4

                # TODO for max accuracy, remove the if & break below? 
                if (dist13 > dist12) and FAST_SEARCH:  # Much faster (3x-10x), but path length is ~1% more 
                   break  
                # note the symmetry of test, since the outer node2 loop will 
                # eventually hit the other points

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

    def get_length_common(self, next_node):
        return sum(( self.dist(n1,n2) for n1, n2 in enumerate(next_node) if n2!=None))

    def get_tour_length(self):
        # n1 = node, n2 = next_node[n1]
        # return sum(( self.dist(n1,n2) for n1, n2 in enumerate(self.next_node)))
        return self.get_length_common(self.next_node)

    def external_tour_length(self, node_list):
        next_node = self.to_next_node_list(node_list)
        # return sum(( self.dist(n1,n2) for n1, n2 in enumerate(next_node)))
        return self.get_length_common(next_node)

    def external_path_length(self, node_list):
        next_node = self.to_next_node_list(node_list)
        return self.get_length_common(next_node[:-1])
        # return sum(( self.dist(n1,n2) for n1, n2 in enumerate(next_node[:-1])))

    def get_edge_counts(self):
        # return (TourEngine.edges.min(), TourEngine.edges.max())
        edges = TourEngine.edges
        ecounts = {}
        for e in edges:
            ecounts[edges[e]] = ecounts.setdefault(edges[e],0) + 1
        return [(cnt, ecounts[cnt]) for cnt in sorted(ecounts)]

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

def chunks(l, n):
    # split a list into chunks of length n
    return [l[i:i+n] for i in range(0, len(l), n)]

def shuffled_paths(node_list, path_len):
    return [random.sample(path, len(path)) for path in chunks(node_list, path_len)]

def z_order_id(x,y):
    # z-order id is interleaving of 16-bit binary strings of the int x & y coordinates
    x, y = int(x), int(y)
    sx = '{:016b}'.format(x) 
    sy = '{:016b}'.format(y)
    return ''.join(i for j in zip(sx,sy) for i in j)  

def z_order_paths(node_list, path_len):
    # TourEngine.nodes = df of id, x, y
    zpaths = []
    for path in chunks(node_list, path_len):
        xs = TourEngine.nodes['x'][path]
        ys = TourEngine.nodes['y'][path]
        z_node = [(z_order_id(x,y), node) for node, x,y in zip(path, xs, ys)]
        z_order_nodes = [node for z, node in sorted(z_node)]
        zpaths.append(z_order_nodes)
    return zpaths
        
def bit_counter_iterator(nbits):
    for  bit_tuple in itertools.product((0,1), repeat=nbits):
        yield bit_tuple

class PathLengthCache:
    def __init__(self, tour_engine):
        self.cache = {}
        self.tour_engine = tour_engine
    def path_length(self, path):
        path = tuple(path)
        #print "PathLengthCache.path_length():", path
        #print "Min/max for path:", min(path),max(path)
        if path not in self.cache:
            self.cache[path] = self.tour_engine.external_path_length(path)
        return self.cache[path]

def unchunk(lst_of_lsts):
    # returns list of lists of nodes into a single concatenated list of nodes
    return sum(lst_of_lsts, [])

def print_tour_len_from_chunks(t1c, t2c, f_tourlen):
    tourlen1 = f_tourlen(unchunk(t1c))
    tourlen2 = f_tourlen(unchunk(t2c))
    print 'REAL LENGTHS:', 'tour1:', round(tourlen1), 'tour2:', round(tourlen2)
    sys.stdout.flush()

def opt_merge_tours(tour1_nodes, tour2_nodes, chunk_length, f_tourlen):
    assert len(tour1_nodes) == len(tour2_nodes), 'Tour lengths differ!'
    t1c = chunks(tour1_nodes, chunk_length)
    t2c = chunks(tour2_nodes, chunk_length)
    n_chunks = len(t1c)
    assert len(t1c) == len(t2c), 'Unequal number of tour chunks!'

    passes = 0
    last_gap = None 
    improving = True
    while improving:
        improving = False
        for i, n in enumerate(random.sample(range(0,n_chunks), n_chunks)):
            tourlen1_noswap = f_tourlen(unchunk(t1c))
            tourlen2_noswap = f_tourlen(unchunk(t2c))
            t1c[n], t2c[n]  = t2c[n], t1c[n] # swap tour chunk n between tour
            tourlen1_swap   = f_tourlen(unchunk(t1c))
            tourlen2_swap   = f_tourlen(unchunk(t2c))
            t1c[n], t2c[n]  = t2c[n], t1c[n] # swap back  
            
            if abs(tourlen1_swap   - tourlen2_swap) <  \
               abs(tourlen1_noswap - tourlen2_noswap): 
                t1c[n], t2c[n] = t2c[n], t1c[n] # swap tour chunk n between tours
                improving = True
                vals = (i, n, 'swap', int(tourlen1_swap), int(tourlen2_swap))
                print '%4i chunk: %4i %6s   tour1: %8i   tour2: %8i' % vals
            else:
                vals = (i, n, '----', int(tourlen1_noswap), int(tourlen2_noswap))
                print '%4i chunk: %4i %6s   tour1: %8i   tour2: %8i' % vals
            sys.stdout.flush()

        passes += 1
        gap = abs(tourlen1_noswap - tourlen2_noswap)
        if last_gap:
            delta_gap = gap - last_gap
        else:
            delta_gap = 0
        last_gap = gap 

        print '\npass:', passes,
        print 'tour1_len:', round(tourlen1_noswap), 'tour2_len:', round(tourlen2_noswap),
        print 'gap:', round(gap), 'delta_gap:', round(delta_gap)
        print 
        sys.stdout.flush()
    return  unchunk(t1c), unchunk(t2c)

def merge_tours(tour1_nodes, tour2_nodes, chunk_length, tour_engine):
    f_plen = tour_engine.external_path_length
    f_tlen = tour_engine.external_tour_length
    tour1_chunks = chunks(tour1_nodes, chunk_length) 
    tour2_chunks = chunks(tour2_nodes, chunk_length)
    # TODO now just splices alternate chunks; shoud it merge more smartly? 
    t1,t2 = [],[]
    for n, (chunk1, chunk2) in enumerate(zip(tour1_chunks, tour2_chunks)):
        print 'chunk_path_lenths',n,'tour1:', int(f_plen(chunk1)), 'tour2:', int(f_plen(chunk2)),

        # DEBUG
        s1=set(chunk1)
        s2=set(chunk2)
        print "chunk_sets:",n,"lenIntersect:", len(s1.intersection(s2)), "lenUnion:", len(s1.union(s2))

        if n % 2 == 0:
            t1.extend(chunk1)
            t2.extend(chunk2)
        else:
            t1.extend(chunk2)
            t2.extend(chunk1)
        #print 'cumulative tour lengths:', int(f_tlen(t1)), int(f_tlen(t2))
    print 'merged tour lengths:',int(f_tlen(t1)), int(f_tlen(t2))
    print "***start NONE check in merge_tours***"
    for n,(a,b) in enumerate(zip(t1,t2)):
        if a==None or b==None:
            print n,a,b
    print "***end NONE check in merge_tours***"
    print "t1, t2 lengths:", len(t1),len(set(t1)), len(t2), len(set(t2))
    sys.stdout.flush()
    return t1, t2


def do_2opt_passes( tour1, tour2, updater, update_path_len, \
                    batch_size = BATCH_SIZE_FULLTOUR, \
                    min_pass_improvement = MIN_PASS_IMPROVEMENT_FULLTOUR):

    lmax_last = int(max(tour1.get_tour_length(), tour2.get_tour_length()))
    t0 = time.time()
    nodes_processed = 0
    pass_improvement = { 0:min_pass_improvement }
    #num_nodes = max(len(tour1.starting_tour), len(tour2.starting_tour))
    improving = True

    while improving:

        for _ in xrange(batch_size):
            updater.next()
            nodes_processed += 1

        l1 = int(tour1.get_tour_length())
        l2 = int(tour2.get_tour_length())
        lmax = max(l1,l2)
        improvement = lmax_last - lmax
        lmax_last = lmax

        pass_num = int(nodes_processed / update_path_len) + 1
        if pass_num not in pass_improvement:
            # started a new pass...
            pass_improvement[pass_num] = 0
            if (pass_improvement[pass_num - 1] < min_pass_improvement) and \
               (pass_improvement[pass_num - 1] >= 0) :
                improving = False
        pass_improvement[pass_num] += improvement

        print "pass:", pass_num, "nodes:", nodes_processed, 
        print "tour1:", l1, "tour2:",l2,
        print "max:",lmax, "imp:",improvement, 
        print "pass_imp:", pass_improvement[pass_num],
        print "secs:", int(time.time()-t0),

        # print "edge counts:", tour1.get_edge_counts(), tour2.get_edge_counts()
        ecounts = tour1.get_edge_counts()
        print "edges:", ecounts
        sys.stdout.flush()

        #print "checking tour lengths"
        #tour1_nodelist  = tour1.get_current_tour_node_list()
        #tour2_nodelist  = tour2.get_current_tour_node_list()
        #print "tour1_length", len(tour1_nodelist), 'uniq:',len(set(tour1_nodelist)),
        #print "tour2_length", len(tour2_nodelist), 'uniq:',len(set(tour2_nodelist))

        # print "FOR DEBUG -- aborting loop"
        # break # TODO FOR DEBUGGING -- so remove thie! 

    print "\nRESULTS ", 
    print "passes:", pass_num, " nodes:", nodes_processed, 
    print " tour1:", l1, " tour2:",l2,
    print " max:",lmax, " secs:", int(time.time()-t0),
    print " 2edges:", ecounts


def main():

    print "\n*** 2-OPT for Traveling Santa Problem ***\n"
    tour_infile     = sys.argv[1] 
    update_path_len = int(sys.argv[2])
    tour_outfile    = sys.argv[3] 
    print "Input  tour file   :", tour_infile
    print "Update path length :", update_path_len
    print "Output tour file   :", tour_outfile
    print
    
    tour1_init, tour2_init = read_tours(tour_infile) 
    assert len(tour1_init)==len(tour2_init)
    tour1 = TourEngine(tour1_init)
    tour2 = TourEngine(tour2_init)

    # cross-splice subtours
    tour1_nodes = tour1.get_current_tour_node_list()
    tour2_nodes = tour2.get_current_tour_node_list()
    tour1_merged, tour2_merged = opt_merge_tours(tour1_nodes, tour2_nodes, update_path_len, 
                                                 tour1.external_tour_length)
    assert len(tour1_merged) == len(tour2_merged)
    assert len(tour1_merged)==len(set(tour1_merged))
    assert len(tour2_merged)==len(set(tour2_merged))

    # do 2opt passes on entirity of both merged tours to improve links between subtours
    tour1.clear_all_edges()
    tour1 = TourEngine(tour1_merged)
    tour2 = TourEngine(tour2_merged)
    print '\nstarting 2opt\n'
    updater = itertools.izip(tour1.tour_update_generator(),
                             tour2.tour_update_generator())
    do_2opt_passes(tour1, tour2, updater, len(tour1_merged),
                   batch_size=BATCH_SIZE_FULLTOUR, 
                   min_pass_improvement=MIN_PASS_IMPROVEMENT_FULLTOUR)

    # write results
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


