# twentysix.py   Jan 4, 2011 by CJH
# 
# This program determines the distinct communities / sub-graphs in the 
# social network challenge data.  Not all nodes/vertices are reachable 
# from all other vertices in the training set. There is one large
# connected community/graph of 1133394 nodes; the remaining 153 nodes are
# scattered across 25 other communities with a few nodes in each of them. 
# Since the 25 communities are small/insignificant, this isn't a big
# discovery. 

import sys
import copy
import random 

TRAINING_FILE = "/home/chefele/SocialNetwork/download/social_train.csv"
MAX_VERTEX_ID = 1133547

def getVertexNeighbors():
    vall = {}  # maps a VertexID to a list of VertexIDs of all links 
    print "Initializing"
    for ix in xrange(1,MAX_VERTEX_ID+1):
        vall[ix] = []
    print "Opening:",TRAINING_FILE
    fin = open(TRAINING_FILE)
    linecounter = 0
    print "Reading lines:"
    for line in fin.readlines():
        linecounter += 1
        if linecounter % 100000 == 0:
            print linecounter,
            sys.stdout.flush()
        tokens = line.split(",")
        vout, vin = ( int(tokens[0]), int(tokens[1]) )
        vall[vin].append(vout)
        vall[vout].append(vin)
    for v in vall:      # remove unused node ids (a few are unused)
        if vall[v]==[]:
            del vall[v]
    print "\nDone reading"
    return vall

def reachableVertices(startVertex, reachedVertices, vertexNeighbors):
    reachedVertices.add(startVertex)
    pendingVertices = set([startVertex])
    while pendingVertices != set():
        # print "Vertices Pending:", len(pendingVertices)
        thisVertex = pendingVertices.pop()
        for neighborVertex in vertexNeighbors[thisVertex]:
            if neighborVertex not in reachedVertices:
                reachedVertices.add(neighborVertex)
                pendingVertices.add(neighborVertex)
    return reachedVertices

def main():
    vertexNeighborsTable = getVertexNeighbors()
    allVertices = set(vertexNeighborsTable.keys())
    remainingVertices = copy.deepcopy(allVertices) 
    reachedVertices = set()
    communityNumber = 0

    while remainingVertices != set() : 
        startVertex = random.choice(list(remainingVertices)) #list(remainingVertices)[0]
        reachedVertices = reachableVertices( startVertex,reachedVertices,vertexNeighborsTable )
        remainingVertices = allVertices - reachedVertices
        communityNumber += 1 
        print "Community:", communityNumber,
        print "Cumulative Vertices Reached:",  len(reachedVertices),
        print "Vertices Remaining:",len(remainingVertices)
        print "Remaining Vertices:"
        for v in remainingVertices:
            print "  ",v
        print
 
    print "Done"

main()


