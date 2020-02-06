# Program to create train & probe sets for Social network challenge
# It picks random nodes for false edges in the graph to balance 1:1 the
# given edges in the 'social_train.csv' datafile
# It then writes 3 files: a probe file, a training file, and a probe+training file
# (the last includes the false edges for training, unlike the original social_train.csv)
#

import copy
import random
import sys

TRAINING_FILE   = "/home/chefele/SocialNetwork/download/social_train.csv"
RANDOM_NUM_GEN_SEED =  1234567  
random.seed(RANDOM_NUM_GEN_SEED)

# Data structures:
# Vins[Vout]: for a node Vout, the set of nodes to which its oubound edges are going 

def printStatus(n, mod):
    if (n % mod) == 0:
        sys.stdout.write(".")
        sys.stdout.flush()

def readVertexConnections(fileName):
    print "\nReading:",fileName
    Vins = {}
    linesRead = 0 
    for line in open(fileName, "r"):
        tokens = [int(token) for token in line.split(",")]
        Vout, Vin = (tokens[0], tokens[1]) 
        Vins.setdefault(Vout,set())
        Vins[Vout].add(Vin)
        linesRead += 1
        printStatus(linesRead, 100000)
    print
    return Vins

def calcEdgeVertexInsList(Vins):
    print "Calculating list of inbound vertices"
    edgeVins=[]
    counter = 0 
    for Vout in Vins:
        edgeVins.extend(list(Vins[Vout]))
        counter += 1
        printStatus(counter, 500)
    print "\n",len(edgeVins),"inbound vertices in list"
    return edgeVins

def vertexDegree(vertex, vertexDict):
        return len(vertexDict[vertex])

def sampleNonEdgeVertices(Vins):
    nonEdgeVins = {}
    edgeVins = calcEdgeVertexInsList(Vins)
    counter = 0 
    print "Sampling non-edges"    
    for Vout in Vins:
        nonEdgeVins[Vout] = set()
        nonEdgeVinsNeeded = vertexDegree(Vout, Vins)  
        for _loop in xrange(nonEdgeVinsNeeded): 
            while True: # randomly pick a nonEdge dest node, retry if fails criteria
                        # not link to self, not in a real edge, not already picked 
                nonEdgeVin = random.choice(edgeVins) # list of Vins with dups, not a set 
                if  (nonEdgeVin!=Vout) and \
                    (nonEdgeVin not in Vins[Vout]) and \
                    (nonEdgeVin not in nonEdgeVins[Vout]):
                    break 
            nonEdgeVins[Vout].add(nonEdgeVin)
        counter += 1
        printStatus(counter, 500)
    print "\nDone sampling non-edges"
    return nonEdgeVins

def calcVoutsFromVins(Vins):
    print "Converting from Vin format to Vout format"
    Vouts = {}
    numVertexes = 0 
    counter = 0 
    for Vout in Vins:
        for Vin in Vins[Vout]:
            Vouts.setdefault(Vin,set())
            Vouts[Vin].add(Vout)
            numVertexes += 1
        counter += 1
        printStatus(counter, 1000)
    print "\n",numVertexes,"vertexes converted"
    return Vouts

def splitTrueFalseTrainProbe(trueVins, falseVins, minOutdegree=2, minIndegree=2):
    trueTrainVins =  trueVins # copy.deepcopy(trueVins)
    trueTrainVouts = calcVoutsFromVins(trueTrainVins)
    falseTrainVins = falseVins
    trueProbeVins, falseProbeVins = ( {},{} )
    lowOutdegree, lowIndegree, counter = (0,0,0)   
    print "Splitting data into training & probe"
    for currentVout in trueTrainVins: # loop through outbound vertices
        if vertexDegree(currentVout, trueTrainVins) < minOutdegree:
            lowOutdegree+=1
            continue
        probeCandidates = \
            [ (tV,fV) for tV,fV in 
              zip( trueTrainVins[currentVout], falseTrainVins[currentVout] ) \
              if vertexDegree(tV, trueTrainVouts) >= minIndegree ]
        if not probeCandidates:
            lowIndegree += 1
            continue

        trueProbeVin, falseProbeVin = random.choice(probeCandidates)
        trueProbeVins[ currentVout] = set([trueProbeVin])
        falseProbeVins[currentVout] = set([falseProbeVin])
        trueTrainVins[ currentVout].remove(trueProbeVin)
        falseTrainVins[currentVout].remove(falseProbeVin)
        trueTrainVouts[trueProbeVin].remove(currentVout)

        counter += 1
        printStatus(counter, 500) 
    print "\nOutbound vertices skipped:",lowOutdegree+lowIndegree,
    print "(",lowIndegree,"due to Low Indegree,",lowOutdegree,"due to Low Outdegree )"
    return trueTrainVins, falseTrainVins, trueProbeVins, falseProbeVins

def printVStats(V):
    print len(V),"Vout nodes"
    numPts = sum( [len(V[Vi]) for Vi in V] )
    print "Tot edges:",numPts
    print
    sys.stdout.flush()
    return None

def writeVertexConnections(trueVins, falseVins, fileName, randomize=False): 
    print "Preparing data to output"
    outLines = []
    lineCounter = 0 
    for currentVout in trueVins:
        for currentVin in trueVins[currentVout]:
            outLine = str(currentVout)+","+str(currentVin)+","+"1\n"
            outLines.append(outLine)
            lineCounter += 1
            printStatus(lineCounter, 100000)
    for currentVout in falseVins:
        for currentVin in falseVins[currentVout]:
            outLine = str(currentVout)+","+str(currentVin)+","+"0\n"
            outLines.append(outLine)
            lineCounter += 1
            printStatus(lineCounter, 100000)
    print 
    if randomize:
        print "Randomly shuffling output"
        random.shuffle(outLines)
    print "Writing to:", fileName
    fout = open(fileName,"w")
    fout.writelines(outLines)
    fout.close()
    print "Finished writing file"

    
# main ========================================================

print "SOCIAL NETWORK CHALLENGE: Program to create train & probe sets" 

trueVins = readVertexConnections(TRAINING_FILE)
falseVins = sampleNonEdgeVertices(trueVins)

print "Copying data..."
trueVinsCopy = copy.deepcopy(trueVins)
falseVinsCopy = copy.deepcopy(falseVins)
print "Done copying data"

trueTrainVins, falseTrainVins, trueProbeVins, falseProbeVins = \
    splitTrueFalseTrainProbe(trueVins, falseVins, minOutdegree=2,minIndegree=2)

writeVertexConnections( trueProbeVins, falseProbeVins, \
                        "social_probe.csv",randomize=True)
writeVertexConnections( trueTrainVins, falseTrainVins, \
                        "social_train_minus_probe.csv", randomize=True)
writeVertexConnections( trueVinsCopy, falseVinsCopy, \
                        "social_train_plus_probe.csv", randomize=True)
print "Finished"

