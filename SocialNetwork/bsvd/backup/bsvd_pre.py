import sys
import random 
import time
import itertools

OUTPUT_FILENAME     = "bsvd_train.csv"
SHUFFLE_OUTPUT_EDGES=  True
NONEDGES_PER_EDGE   =  2  # 1 for 50%/50%; vary this to optimize?

TRAINING_DATAFILE   = "/home/chefele/SocialNetwork/download/social_train.csv"
#TRAINING_DATAFILE   = "/home/chefele/SocialNetwork/data/social_train_short.csv"
TEST_DATAFILE       = "/home/chefele/SocialNetwork/download/social_test.txt"
 
MAX_VERTEX_ID       =  1133547
PRINT_MOD           =  100000 # updates status after every so many edges processed 
RANDOM_NUM_GEN_SEED =  1234567  
random.seed(RANDOM_NUM_GEN_SEED)



def printStatus(n):
    if n % PRINT_MOD == 0:
        sys.stdout.write(".")
        sys.stdout.flush()

def edgeVertexOuts(edgeTable):
    return edgeTable["Vout"]

def edgeVertexIns(edgeTable):
    return edgeTable["Vin"]

def calcEdgeHash(Vout,Vin):
    return Vout*(MAX_VERTEX_ID+1) + Vin 

def calcExistingEdgeSet(edgeTable):
    Vouts = edgeVertexOuts(edgeTable)
    Vins  = edgeVertexIns( edgeTable)
    assert len(Vouts) == len(Vins)
    print " Creating a set of all graph edges"
    existingEdgeSet = {}
    for edgeNum, Vout in enumerate(Vouts):
        Vin = Vins[edgeNum]
        edge = calcEdgeHash(Vout,Vin)
        existingEdgeSet[edge]=1  
        printStatus(edgeNum)
    print 
    return existingEdgeSet

def sampleNonEdges(nSamplesNeeded, edgeTable):
    # sample vertices of non-edges independently & resample if hit an existing edge 
    print "Generating:",nSamplesNeeded,"non-edge samples"
    nonEdgeVouts= [0]*nSamplesNeeded  #jarray.zeros(nSamplesNeeded,"i")
    nonEdgeVins = [0]*nSamplesNeeded  #jarray.zeros(nSamplesNeeded,"i")
    existingEdgeVouts   = edgeVertexOuts(edgeTable)
    existingEdgeVins    = edgeVertexIns(edgeTable)
    existingEdgeSet     = calcExistingEdgeSet(edgeTable)   
    print " Creating the sample of graph non-edges"
    nSampled = 0 
    while nSampled < nSamplesNeeded:
        while True:
            nonEdgeVout = random.choice(existingEdgeVouts) 
            nonEdgeVin  = random.choice(existingEdgeVins)
            nonEdge = calcEdgeHash(nonEdgeVout,nonEdgeVin) 
            if (nonEdge not in existingEdgeSet) and (nonEdgeVout != nonEdgeVin):
                break
        nonEdgeVouts[nSampled] = nonEdgeVout 
        nonEdgeVins[nSampled] = nonEdgeVin
        printStatus(nSampled)
        nSampled += 1
    print
    sampledNonEdgeTable = { "Vout":nonEdgeVouts, "Vin":nonEdgeVins }
    return sampledNonEdgeTable

def readEdgeFile(filename):
    print "Reading:", filename
    fin=open(filename,"r")
    lines = fin.readlines()
    fin.close()
    print "Read:", len(lines),"lines"
    print "Parsing read lines"
    Vouts=[0]*len(lines) #jarray.zeros(len(lines),"i")
    Vins= [0]*len(lines) #jarray.zeros(len(lines),"i")
    for lineNum, line in enumerate(lines):
        tokens = line.split(",")
        Vouts[lineNum] = int(tokens[0])
        Vins[lineNum] =  int(tokens[1]) 
        printStatus(lineNum)
    print
    existingEdgeTable = { "Vout":Vouts, "Vin":Vins }
    return existingEdgeTable

def writeEdgeFile(filename, outputDataTuples):
    print "Writing:", filename
    fout=open(filename,"w")
    for lineNum, outData in enumerate(outputDataTuples):
        Vout, Vin, Prob = outData
        fout.write(str(Vout)+","+str(Vin)+","+str(Prob)+"\n")
        printStatus(lineNum)
    fout.close()
    print
    print "Writing complete"

def makeTuples(a,b,c):
    print "Forming tuples (slow!)"
    outList = len(a) * [()]
    for lineNum, _a in enumerate(a):
        outList[lineNum] = ( a[lineNum],b[lineNum],c[lineNum] )
        printStatus(lineNum)
    print
    return outList
        
def makeOutputDataTuples(edgeTable, sampNonEdges):
    edgeVout = edgeVertexOuts(edgeTable)
    edgeVin  = edgeVertexIns(edgeTable)
    edgeProb = [1] * len(edgeVertexOuts(edgeTable))
    nonEdgeVout = edgeVertexOuts(sampNonEdges)
    nonEdgeVin  = edgeVertexIns(sampNonEdges)
    nonEdgeProb = [0] * len(edgeVertexOuts(sampNonEdges))
    if SHUFFLE_OUTPUT_EDGES:
        outData = makeTuples( edgeVout+nonEdgeVout, edgeVin+nonEdgeVin, edgeProb+nonEdgeProb)
        print "Randomly shuffling output data"
        random.shuffle(outData)
        return outData
    else:
        Vouts = itertools.chain(edgeVout, nonEdgeVout)
        Vins = itertools.chain(edgeVin, nonEdgeVin)
        Probs = itertools.chain(edgeProb, nonEdgeProb)
        return itertools.izip(Vouts,Vins,Probs)
    
def main():
    print "\n*** BSVD Pre-processor ***\n"
    edgeTable = readEdgeFile(TRAINING_DATAFILE)
    numEdges = len(edgeVertexOuts(edgeTable))
    numNonEdges = numEdges * NONEDGES_PER_EDGE
    sampNonEdges = sampleNonEdges(numNonEdges, edgeTable)
    outData = makeOutputDataTuples(edgeTable, sampNonEdges)
    writeEdgeFile(OUTPUT_FILENAME, outData)
    print "Done"

main()



