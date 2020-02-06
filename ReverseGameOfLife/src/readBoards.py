import pandas
import numpy as np

TEST_FILE  = '../download/test.csv'
TRAIN_FILE = '../download/train.csv'

BOARD_ROWS  = 20
BOARD_COLS  = 20
BOARD_SHAPE = (BOARD_ROWS, BOARD_COLS)
BOARD_CELLS = BOARD_ROWS * BOARD_COLS

def colNames(tag): 
    # returns a list of numbered column names, e.g. ['stop.1','stop.2',...]
    return [ tag+'.{col}'.format(col=col) for col in xrange(1,BOARD_CELLS+1)]

def boardFromRowCols(row, cols):
    binary_array = np.array(row[cols]).reshape(BOARD_SHAPE, order='F') 
    return binary_array == 1  # returns boolean array 
    
def readBoards(filename, includeStartBoard=False):
    df = pandas.read_csv(filename)
    nrows, ncols = df.shape
    rows = (df.irow(r) for r in xrange(nrows))
    startColNames = colNames('start')
    stopColNames  = colNames('stop' ) 
    for row in rows:
        if includeStartBoard:
            startBoard = boardFromRowCols(row, startColNames)
            stopBoard  = boardFromRowCols(row, stopColNames) 
            yield (row['id'], row['delta'], startBoard, stopBoard)
        else:
            stopBoard  = boardFromRowCols(row, colNames('stop' )) 
            yield (row['id'], row['delta'], stopBoard)

def readTestBoards():
    # iterator returning: id, delta, stopBoard
    return readBoards(TEST_FILE, includeStartBoard=False)

def readTrainBoards():
    # iterator returning: id, delta, startBoard, stopBoard
    return readBoards(TRAIN_FILE, includeStartBoard=True)

def print_board(board):
    print board*1 # converts a board of booleans to 0/1 for easier printing 

def do_tests():
    print 'reading:', TRAIN_FILE
    for rid, delta, start_board, stop_board  in readTrainBoards():
        print "\n***", "id:", rid, "delta:", delta,"***\n"
        print "START BOARD"
        print_board(start_board)
        print "STOP BOARD"
        print_board(stop_board)

if __name__ == '__main__':
    do_tests()
