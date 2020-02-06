# link prediction via path-length metrics  by  CJH 1/11/2011

import sys
import random
import time
from math import log
import dijkstra

TRAINING_INFILENAME   = "/home/chefele/SocialNetwork/data/social_train_minus_probe.csv"
#PROBE_INFILENAME      = "/home/chefele/SocialNetwork/data/social_probe.csv"
PROBE_INFILENAME      = "/home/chefele/SocialNetwork/data/social_probe_sample10K.csv"
TEST_INFILENAME       = "/home/chefele/SocialNetwork/download/social_test.txt"
TRAINING_OUTFILENAME  = "paths_train_minus_probe_out.csv"
PROBE_OUTFILENAME     = "paths_probe_out.csv"
TEST_OUTFILENAME      = "paths_test_out.csv"

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

def boYangMetric(Vout,Vin, graphStruct):
    Vstart = graphStruct.graphDict[Vout]
    Vend   = graphStruct.graphDict[Vin]
    distsFromTo = dijkstra.ShortestPaths(graphStruct.graphList, Vstart, Vend)
    distsToFrom = dijkstra.ShortestPaths(graphStruct.graphList, Vend, Vstart)
    tot=1.0
    for vName in set(distsFromTo.keys()).intersection(set(distsToFrom.keys())) : 
        tot += pow(2,  min(20,distsFromTo[vName])+min(20,distsToFrom[vName]) )
    return 1.0/tot
    
metricFunctions = [boYangMetric] 

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
    metricCols = calcMetricColumnsByRows(metricFunctions, inData, adjMatrix)
    outData = pasteEdgeTableColumns( metricCols, inData) 
    writeCSV(outData, outFileName, header=True)
    print

def makeVertexName(v):
    return "V"+str(v)

class GraphStructure:
    def __init__(self, graphList, graphDict):
        self.graphList = graphList
        self.graphDict = graphDict

def makeGraphFromAdjacencyMatrix(adjM): #convert format to that needed by shortest-path algo
    graphDict = {}
    graphList = []
    loops=0
    for vertex in adjM:
        vertexName = makeVertexName(vertex)
        neighborVertices = [(makeVertexName(v),1) for v in adjM[vertex]] #(Vname,dist=1) 
        newVertex = dijkstra.Vertex(vertexName, neighborVertices)
        graphList.append(newVertex)
        graphDict[vertex] = newVertex
        loops+=1
        printStatusPercent(loops, len(adjM), 25000)
    return GraphStructure( graphList, graphDict)


# =============  MAIN ==================
print "\n**** Metrics Calculation ****\n"

probeEdgeTable    = readFileWithoutMetrics(PROBE_INFILENAME, colNames=["Vout","Vin","Prob"])
testEdgeTable     = readFileWithoutMetrics(TEST_INFILENAME,  colNames=["Vout","Vin"])
trainingEdgeTable = readFileWithoutMetrics(TRAINING_INFILENAME, colNames=["Vout","Vin","Prob"])

adjMatrix = makeAdjacencyMatrix(trainingEdgeTable, addForwardLinks=True, addReverseLinks=True) 
graph = makeGraphFromAdjacencyMatrix(adjMatrix)
#print "***DEBUG PRINTS***"
#print adjMatrix[69] # debug; result=set([302115, 569172, 731015])
#print graph[69]

writeFileWithMetrics(probeEdgeTable,    graph, PROBE_OUTFILENAME)
writeFileWithMetrics(testEdgeTable,     graph, TEST_OUTFILENAME)
#writeFileWithMetrics(trainingEdgeTable, adjMatrix, TRAINING_OUTFILENAME)

print "\nDone.\n"

