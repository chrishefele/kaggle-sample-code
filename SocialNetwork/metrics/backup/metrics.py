#
import sys
import random
from math import log

TRAINING_INFILENAME   = "/home/chefele/SocialNetwork/data/social_train_minus_probe.csv"
PROBE_INFILENAME      = "/home/chefele/SocialNetwork/data/social_probe.csv"
TEST_INFILENAME       = "/home/chefele/SocialNetwork/download/social_test.txt"
TRAINING_OUTFILENAME  = "metrics_train_minus_probe_out.csv"
PROBE_OUTFILENAME     = "metrics_probe_out.csv"
TEST_OUTFILENAME      = "metrics_test_out.csv"

MAX_VERTEX_ID       =  1133547
PRINT_MOD           =  200000 # updates status after every so many edges processed 

def printStatus(n):
    if n % PRINT_MOD == 0:
        sys.stdout.write(".")
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
        printStatus(lineNum)
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

def vertexDegree(V, adjacencyMatrix):
    return len(adjacencyMatrix[V]) 

def commonNeighbors(V1, V2, adjacencyMatrix):
    return adjacencyMatrix[V1].intersection(adjacencyMatrix[V2])

def allNeighbors(V1, V2, adjacencyMatrix):
    return adjacencyMatrix[V1].union(adjacencyMatrix[V2])

def numCommonNeighbors(V1, V2, adjacencyMatrix):
    return len( commonNeighbors(V1, V2, adjacencyMatrix) )

def numAllNeighbors(V1, V2, adjacencyMatrix):
    return len( allNeighbors(V1, V2, adjacencyMatrix) ) 

def Jaccard(V1, V2, adjM):
    # adjM = adjacencyMatrix 
    return ( float(numCommonNeighbors(V1,V2,adjM)) / numAllNeighbors(V1,V2, adjM) )

def AdamicAdar(V1, V2, adjM): 
    # adjM = adjacencyMatrix
    commonNbrs = commonNeighbors(V1,V2,adjM)
    return sum([ 1.0/log(vertexDegree(V,adjM)) for V in commonNbrs ])

def PrefAttachment(V1, V2, adjM):
    # adjM = adjacencyMatrix
    return (vertexDegree(V1,adjM)*vertexDegree(V2,adjM))

def OutnodeInvDegree(V1, V2, adjM): 
    if vertexDegree(V1,adjM) == 0:
        return 0
    else: 
        return (1.0/vertexDegree(V1,adjM))

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
        printStatus(edgeNum)
    print 
    return { metricName:metricColumn } # dict with 1 column entry 

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

def writeFileWithMetrics(inData, adjMatrix, outFileName):
    print "Calculating metrics to write to:",outFileName
    # Jaccard is slow to compute when outputting training set 
    # so use the appropriate list of metrics below for your case
    metricFunctions = [ OutnodeInvDegree, PrefAttachment, \
                        numCommonNeighbors, AdamicAdar, Jaccard]
    # metricFunctions = [ OutnodeInvDegree, PrefAttachment, numCommonNeighbors, AdamicAdar]

    print "Metrics to calculate:", [metric.__name__ for metric in metricFunctions]
    metricCols = {}
    for metricFunction in metricFunctions: 
        metricCol = calcMetricColumn( metricFunction, inData, adjMatrix ) 
        metricCols = pasteEdgeTableColumns( metricCols, metricCol ) 
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
writeFileWithMetrics(trainingEdgeTable, adjMatrix, TRAINING_OUTFILENAME)

print "\nDone.\n"

