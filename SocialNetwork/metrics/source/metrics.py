# link prediction via vertex-based metrics  by  CJH 1/7/2011

import sys
import random
import time
from math import log

TRAINING_INFILENAME   = "/home/chefele/SocialNetwork/data/social_train_minus_probe.csv"
#PROBE_INFILENAME      = "/home/chefele/SocialNetwork/data/social_probe.csv"
PROBE_INFILENAME      = "/home/chefele/SocialNetwork/data/social_probe_sample10K.csv"
TEST_INFILENAME       = "/home/chefele/SocialNetwork/download/social_test.txt"
TRAINING_OUTFILENAME  = "metrics_train_minus_probe_out.csv"
PROBE_OUTFILENAME     = "metrics_probe_out.csv"
TEST_OUTFILENAME      = "metrics_test_out.csv"

MAX_VERTEX_ID       =  1133547
PRINT_MOD           =  200000 # updates status after every so many edges processed 
_timeStart          =  time.time()

def printStatus(n, printMod=PRINT_MOD):
    if n % printMod == 0:
        sys.stdout.write(".")
        sys.stdout.flush()

def printStatusPercent(n,totalItems, updateMod=1):
    if n % updateMod ==0:
        pct = 100.0*float(n)/totalItems
        print " @",n,"out of", totalItems,"(",pct,"% done)",
        print (time.time()-_timeStart)/60.0,"min"
        sys.stdout.flush()

def readCSV(fileName, header=False, colNewNames=[]):
    print "Opening file:",[fileName]
    fin=open(fileName,"r")
    numCols = len(fin.readline().split(","))
    fin.close()
    fin=open(fileName,"r")
    if header:
        headerLine=fin.readline()
        colNames = [ colName.strip() for colName in headerLine.split(",") ]
    else:
        colNames = ["COL"+str(colNum) for colNum in xrange(1,numCols+1)]
    if colNewNames:
        assert len(colNewNames) == numCols
        colNames = colNewNames
    print "Found ",numCols, "columns. Will use column names:", colNames
    #
    lines = fin.readlines()
    fin.close()
    print "Parsing read data"
    outData = {}
    for colName in colNames:
        outData[colName]=[]
    for lineNum, line in enumerate(lines):
        intTokens = [int(token) for token in line.split(",")]
        for colName, intToken in zip(colNames,intTokens):
            outData[colName].append(intToken)
        printStatusPercent(lineNum, len(lines), 1000000)
    print
    return outData

def writeCSV(dataColumns, filename, header=True):
    print "Writing to file: ",[filename] 
    fout = open(filename,"w")
    colNames = set(dataColumns.keys())
    colNames.remove("Vout")
    colNames.remove("Vin")
    colNames = ["Vout","Vin"] + sorted(list( colNames ))
    print "Column names:", colNames
    if header:
        fout.write(colNames[0])
        for colName in colNames[1:]:
            fout.write(","+colName)
        fout.write("\n")
    for lineNum in xrange( len(dataColumns[colNames[0]]) ):
        fout.write( str(dataColumns[colNames[0]][lineNum]) ) 
        for colName in colNames[1:]:
            fout.write( ","+str(dataColumns[colName][lineNum]) )
        fout.write("\n")
        printStatus(lineNum)
    print
    fout.close()

def edgeVertexOuts(edgeTable):
    return edgeTable["Vout"]

def edgeVertexIns(edgeTable):
    return edgeTable["Vin"]

def edgeProbs(edgeTable):
    return edgeTable["Prob"]

def makeAdjacencyMatrix(edgeTable, addForwardLinks=True, addReverseLinks=True):
    print "Calculating vertex adjacency matrix"
    print "Initializing adjacency matrix for each vertex"
    adjacencyMatrix={}    
    for V in xrange(1,MAX_VERTEX_ID+1):
        adjacencyMatrix[V]=set() 
        printStatus(V)
    print
    print "Calculating adjacency matrix from graph edges"
    if addForwardLinks:
        print "Forward links being added to matrix"
    if addReverseLinks:
        print "Reverse links being added to matrix"
    assert addForwardLinks or addReverseLinks
    Vouts = edgeVertexOuts(edgeTable)
    Vins  = edgeVertexIns(edgeTable)
    Probs = edgeProbs(edgeTable)
    for edgeNum, Vout in enumerate(Vouts):
        Vin = Vins[edgeNum]
        Prob = Probs[edgeNum]
        if Prob==1: # for true edges 
            if addForwardLinks:
                adjacencyMatrix[Vout].add(Vin) 
            if addReverseLinks: 
                adjacencyMatrix[Vin].add(Vout)
        else:
            pass # Prob=0 means false edge, so don't tabulate it
        printStatus(edgeNum)  
    print "\n"
    return adjacencyMatrix


def vertexNeighbors(V, adjacencyMatrix):
    return adjacencyMatrix[V]

_nbrsNbrsCache = {}
MAX_CACHE_SIZE = 100
def neighborsNeighbors(V, adjacencyMatrix):
    if V not in _nbrsNbrsCache: 
        if len(_nbrsNbrsCache)>MAX_CACHE_SIZE: # make room for new calculated value
            del _nbrsNbrsCache[ random.choice(_nbrsNbrsCache.keys()) ]
        # calculate new value & cache it 
        nbrsNbrs = set()
        for neighbor in vertexNeighbors(V, adjacencyMatrix):
            nbrsNbrs = nbrsNbrs.union( vertexNeighbors(neighbor, adjacencyMatrix) )
        _nbrsNbrsCache[V] = nbrsNbrs
    return _nbrsNbrsCache[V]

def vertexDegree(V, adjacencyMatrix):
    return len(adjacencyMatrix[V]) 

def commonNeighbors(V1, V2, adjacencyMatrix):
    return adjacencyMatrix[V1].intersection( adjacencyMatrix[V2])

def commonNeighborsNeighbors(V1, V2, adjacencyMatrix):
    return adjacencyMatrix[V1].intersection( neighborsNeighbors(V2,adjacencyMatrix) )

def allNeighbors(V1, V2, adjacencyMatrix):
    return adjacencyMatrix[V1].union(adjacencyMatrix[V2])

def allNeighborsNeighbors(V1, V2, adjacencyMatrix):
    return adjacencyMatrix[V1].union( neighborsNeighbors(V2,adjacencyMatrix) )

def numCommonNeighbors(V1, V2, adjacencyMatrix):
    return len( commonNeighbors(V1, V2, adjacencyMatrix) )

def numCommonNeighborsNeighbors(V1, V2, adjacencyMatrix):
    """numCommonNeighborsNeighbors"""
    return len( commonNeighborsNeighbors(V1, V2, adjacencyMatrix) )

def numAllNeighbors(V1, V2, adjacencyMatrix):
    return len( allNeighbors(V1, V2, adjacencyMatrix) ) 

def numAllNeighborsNeighbors(V1, V2, adjacencyMatrix):
    """numAllNeighborsNeighbors"""
    return len( allNeighborsNeighbors(V1, V2, adjacencyMatrix) ) 

def Jaccard(V1, V2, adjM):
    # adjM = adjacencyMatrix 
    return ( float(numCommonNeighbors(V1,V2,adjM)) / numAllNeighbors(V1,V2, adjM) )

def JaccardNeighborsNeighbors(V1, V2, adjM):
    """JaccardNeighborsNeighbors"""
    # adjM = adjacencyMatrix 
    return ( float(numCommonNeighborsNeighbors(V1,V2,adjM)) \
                 / numAllNeighborsNeighbors(V1,V2, adjM) )

def AdamicAdar(V1, V2, adjM): 
    # adjM = adjacencyMatrix
    commonNbrs = commonNeighbors(V1,V2,adjM)
    return sum([ 1.0/log(1+vertexDegree(V,adjM)) for V in commonNbrs ])

def AdamicAdarNeighborsNeighbors(V1, V2, adjM): 
    """AdamicAdarNeighborsNeighbors"""
    # adjM = adjacencyMatrix
    commonNbrs = commonNeighborsNeighbors(V1,V2,adjM)
    return sum([ 1.0/log(1+vertexDegree(V,adjM)) for V in commonNbrs ])


def PrefAttachment(V1, V2, adjM):
    # adjM = adjacencyMatrix
    return (vertexDegree(V1,adjM)*vertexDegree(V2,adjM))

def OutnodeInvDegree(V1, V2, adjM): 
    if vertexDegree(V1,adjM) == 0:
        return 0
    else: 
        return (1.0/vertexDegree(V1,adjM))

def OutnodeDegree(V1, V2, adjM): 
    return vertexDegree(V1,adjM)

def reverseMetric(metricFunction):
    def reversedMetricFunction(V1,V2, adjM):
        return metricFunction(V2, V1, adjM)
    reversedMetricFunction.__name__ = "reversed_"+metricFunction.__name__
    return reversedMetricFunction

def pasteEdgeTableColumns(edgeTable1, edgeTable2):
    # group 2 seperate dicts with distinct names(keys) together into one dict 
    assert set(edgeTable1.keys()).intersection(set(edgeTable2.keys())) == set()
    return dict( edgeTable1.items() + edgeTable2.items() )

def readFileWithoutMetrics(inFileName, colNames=[]):
    print "Reading from:",inFileName
    edgeTable = readCSV(inFileName, header=False, colNewNames=colNames)
    numEdges = len( edgeVertexOuts(edgeTable) )
    print "Edges read:", numEdges,"\n"
    return edgeTable

def calcMetricColumn(metricFunction, edgeTable, adjacencyMatrix): 
    metricName = metricFunction.__name__
    print "Calculating metric:",metricName
    Vouts = edgeVertexOuts(edgeTable)
    Vins  = edgeVertexIns( edgeTable)
    metricColumn = []
    for edgeNum, Vout in enumerate(Vouts):
        Vin = Vins[edgeNum]
        metric = metricFunction(Vout, Vin, adjacencyMatrix)
        metricColumn.append(metric)
        printStatusPercent(edgeNum, len(Vouts), 1)
    print 
    return { metricName:metricColumn } # dict with 1 column entry 


metricFunctions =     [ OutnodeInvDegree, \
                        OutnodeDegree,    \
                        PrefAttachment,   \
                        numCommonNeighbors, \
                        numCommonNeighborsNeighbors,  \
                        reverseMetric(numCommonNeighborsNeighbors), \
                        numAllNeighborsNeighbors, \
                        reverseMetric(numAllNeighborsNeighbors), \
                        AdamicAdar, \
                        AdamicAdarNeighborsNeighbors,  \
                        reverseMetric(AdamicAdarNeighborsNeighbors), \
                        Jaccard,  \
                        JaccardNeighborsNeighbors,  \
                        reverseMetric(JaccardNeighborsNeighbors) \
                      ]

def calcMetricColumnsByRows(metricFuncs, edgeTable, adjacencyMatrix):
    _timeStart = time.time()
    outData = {}
    for metricFunction in metricFuncs:
        outData[metricFunction.__name__] = []
    Vouts = edgeVertexOuts(edgeTable)
    Vins  = edgeVertexIns( edgeTable)
    for rowNum,(Vout,Vin) in enumerate( zip(Vouts,Vins) ): 
        for metricFunction in metricFuncs:
            metricValue = metricFunction(Vout,Vin,adjacencyMatrix)
            outData[metricFunction.__name__].append(metricValue)
        printStatusPercent(rowNum, len(Vouts), 1)
    print 
    return outData # dict with entries for each metric  


def writeFileWithMetrics(inData, adjMatrix, outFileName):
    print "Calculating metrics to write to:",outFileName
    print "Metrics to calculate:", [metric.__name__ for metric in metricFunctions]
    """
    metricCols = {}
    for metricFunction in metricFunctions: 
        metricCol = calcMetricColumn( metricFunction, inData, adjMatrix ) 
        metricCols = pasteEdgeTableColumns( metricCols, metricCol ) 
    """
    metricCols = calcMetricColumnsByRows(metricFunctions, inData, adjMatrix)
    outData = pasteEdgeTableColumns( metricCols, inData) 
    writeCSV(outData, outFileName, header=True)
    print

# =============  MAIN ==================
print "\n**** Metrics Calculation ****\n"

probeEdgeTable    = readFileWithoutMetrics(PROBE_INFILENAME, colNames=["Vout","Vin","Prob"])
testEdgeTable     = readFileWithoutMetrics(TEST_INFILENAME,  colNames=["Vout","Vin"])
trainingEdgeTable = readFileWithoutMetrics(TRAINING_INFILENAME, colNames=["Vout","Vin","Prob"])

adjMatrix = makeAdjacencyMatrix(trainingEdgeTable, addForwardLinks=True, addReverseLinks=True) 
# print adjMatrix[69] # debug; result=set([302115, 569172, 731015])

writeFileWithMetrics(probeEdgeTable,    adjMatrix, PROBE_OUTFILENAME)
writeFileWithMetrics(testEdgeTable,     adjMatrix, TEST_OUTFILENAME)
#writeFileWithMetrics(trainingEdgeTable, adjMatrix, TRAINING_OUTFILENAME)

print "\nDone.\n"

