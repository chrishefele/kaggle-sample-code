from scipy.signal import convolve2d
import numpy 
import itertools
import collections
import sys

NROWS = int(sys.argv[1])
NCOLS = int(sys.argv[2])

KERNEL = numpy.ones((3,3))

def lifeStep(board):
    nbrs_count = convolve2d(board, KERNEL, mode='same', fillvalue=0) - board
    return (nbrs_count==3) | (board & (nbrs_count==2))

def boardString(board):  
    rowStrings = []
    for row in board:
        rowStrings.append(''.join(['X' if col else 'o' for col in row]))
    return '_'.join(rowStrings)

def boardHash(board):
    return hash(board.tostring())

def startPatterns():
    return itertools.product((False,True), repeat=NROWS*NCOLS)

def getBoardIndegrees():
    fixed_points = 0 
    board_indegree = collections.defaultdict(int)
    for startPattern in startPatterns():
        board = numpy.array(startPattern, dtype=bool).reshape((NROWS, NCOLS))
        startBoard = boardHash(         board )
        stopBoard  = boardHash(lifeStep(board))
        _ = board_indegree[startBoard] # creates board if not already there
        board_indegree[stopBoard] += 1
        if startBoard == stopBoard:
            fixed_points += 1
    print "Fixed points:", fixed_points
    return board_indegree

def boardIndegreeHist(board_indegree):
    indegree_counts = collections.defaultdict(int)
    for board in board_indegree:
        indegree = board_indegree[board]
        indegree_counts[indegree] += 1 
    return indegree_counts

print 
print "Rows:", NROWS, "Cols:", NCOLS, "Est Boards:", pow(2,NROWS*NCOLS)
print "calculating..."
bid = getBoardIndegrees()
print
print "Total boards found:", len(bid)
print "\n***Board Indegree Histograms***"
indegree_counts = boardIndegreeHist(bid)
for degree in sorted(indegree_counts):
    print 'indegree:', degree, 'count:', indegree_counts[degree]

