from scipy.signal import convolve2d
import numpy 
import itertools

NROWS = 3
NCOLS = 3
GRAPH_FILE  = 'transitionGraph.gdf'

# graph node colors
RED         = "'255,0,0'"
TOMATO      = "'255,99,71'"
BLUE        = "'0,0,255'"
LIGHT_BLUE  = "'135,206,250'"
KAGGLE_BLUE = "'32,190,255'"
WHITE       = "'255,255,255'"

KERNEL = numpy.ones((3,3))

def lifeStep(board):
    nbrs_count = convolve2d(board, KERNEL, mode='same', fillvalue=0) - board
    return (nbrs_count==3) | (board & (nbrs_count==2))

def boardString(board):  
    rowStrings = []
    for row in board:
        rowStrings.append(''.join(['X' if col else 'o' for col in row]))
    return '_'.join(rowStrings)

def startPatterns():
    return itertools.product((False,True), repeat=NROWS*NCOLS)

def makeGraphFile(fname):
    fout = open(fname,'w')

    # process nodes
    fout.write('nodedef> name VARCHAR, color VARCHAR, label VARCHAR\n')
    for startPattern in startPatterns():
        board = numpy.array(startPattern, dtype=bool).reshape((NROWS, NCOLS))
        startBoard, stopBoard = boardString(board), boardString(lifeStep(board))
        if startBoard != stopBoard:
            outstring = ','.join([startBoard, KAGGLE_BLUE, startBoard]) 
        else:
            outstring = ','.join([startBoard, KAGGLE_BLUE, startBoard]) # fixed point node
        fout.write(outstring+'\n')

    # process edges between nodes
    fout.write('edgedef> node1 VARCHAR, node2 VARCHAR\n')
    for startPattern in startPatterns():
        board = numpy.array(startPattern, dtype=bool).reshape((NROWS, NCOLS))
        startBoard, stopBoard = boardString(board), boardString(lifeStep(board))
        outstring = ','.join([startBoard, stopBoard]) 
        fout.write(outstring+'\n')

makeGraphFile(GRAPH_FILE)
print 'wrote graph to:', GRAPH_FILE

# .GDF format needs:
# nodedef> name, style 
# team_12345, 1
# team_4567,  2
# edgedef> node1,node2
# team_12345,team_4567
#

