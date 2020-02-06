import pandas
import numpy as np
from   tools import create_blank, print_board, board_rows_str
from search import Search
import copy 

TEST_FILE  = '../../download/test.csv'
TRAIN_FILE = '../../download/train.csv'

BOARD_ROWS  = 20
BOARD_COLS  = 20
BOARD_SHAPE = (BOARD_ROWS, BOARD_COLS)
BOARD_CELLS = BOARD_ROWS * BOARD_COLS

def colNames(tag): 
    return [ tag+'.{col}'.format(col=col) for col in xrange(1,BOARD_CELLS+1)]

def boardDiffs(board1, board2):
    diffs = 0
    for x in range(BOARD_ROWS):
        for y in range(BOARD_COLS):
            if board1[x][y] != board2[x][y]:
                diffs += 1
    return diffs

def boardFromArray(arr):
    # creates board from numpy 1/0 array
    y, x = arr.shape
    board = create_blank(x,y) # includes 1-cell border set to 0 
    for j in range(y):
        for i in range(x):
            board[j][i] = arr[j][i] == 1
    return board

def boardFromRowCols(row, cols):
        boardArray = np.array(row[cols]).reshape(BOARD_SHAPE, order='F')
        return boardFromArray(boardArray)
    
def rowColsFromBoard(board, cols):
        pass # TODO

def readBoards(filename, includeStartBoard=False):
    df = pandas.read_csv(filename)
    nrows, ncols = df.shape
    rows = (df.irow(r) for r in xrange(nrows))
    for row in rows:
        if includeStartBoard:
            startBoard = boardFromRowCols(row, colNames('start'))
            stopBoard  = boardFromRowCols(row, colNames('stop' )) 
            yield (row['id'], row['delta'], startBoard, stopBoard)
        else:
            stopBoard  = boardFromRowCols(row, colNames('stop' )) 
            yield (row['id'], row['delta'], stopBoard)


def ataviseBoard(stopBoard, startBoard):
    candidate = copy.deepcopy(stopBoard)
    search = Search(stopBoard, candidate=candidate)
    needy_initial = search.total_needy
    needy_min = needy_initial
    loops = 0
    while search.total_needy >0:
        search.use_jittery()
        #search.use_pogo()
        needy_min = min(needy_min, search.total_needy)
        loops += 1
        if loops > 1000:
            break
    needy_final = search.total_needy

    print "[ataviseBoard] ",
    #print "initial_needy: %6i"  % needy_initial,
    print "final_needy: %6i"    % needy_final,
    print "min_needy: %6i"      % needy_min,
    print "loops: %8i"          % loops, 
    print "initialDiffs: %6i"   % boardDiffs(startBoard, search.candidate),
    print "endingDiffs:  %6i"   % boardDiffs(startBoard, stopBoard)

def main():
    print 'reading:', TRAIN_FILE

    for rid, delta, start_board, stop_board  in readBoards(TRAIN_FILE, includeStartBoard=True):
        print "\n***", "id:", rid, "delta:", delta,"***\n"

        print "START BOARD"
        print_board(start_board)
        start_rows = board_rows_str(start_board)
        print

        print "STOP BOARD"
        print_board(stop_board)
        stop_rows  = board_rows_str(stop_board)
        print

        for row in zip(start_rows, stop_rows):
            print row
        print

        if delta == 1:
            print "DELTA==1"
            print "id:", rid, 
            ataviseBoard(stop_board, start_board)

main()
