import numpy 
from lifeStep import lifeStep

BOARD_ROWS  = 20
BOARD_COLS  = 20
BOARD_SHAPE = (BOARD_ROWS, BOARD_COLS)
BOARD_CELLS = BOARD_ROWS * BOARD_COLS

BURN_IN_STEPS = 5

RANDOM_SEED  = 424242
# numpy.random.seed(seed=RANDOM_SEED)

# NOTE I commented-out the setting of the random seed because
# I was using training loops via shell scripts, Over repeated
# runs via shell scripts, you can't start with the same seed; 
# otherwise all randomly generated patterns will
# just reoccur & no *new* patterns will be learned.
# Same holds true for executing instances in parallel.
# Normally, we would just set the seed for repeatability, 

def randomInitBoard(sideLength):
    fillFraction = numpy.random.uniform(low=0.01, high=0.99, size=1)
    board = numpy.random.binomial(n=1, p=fillFraction, size=(sideLength, sideLength)) 
    return board == 1

def randomStartStopBoards(sideLength=BOARD_ROWS):
    board = randomInitBoard(sideLength)
    for i in xrange(BURN_IN_STEPS):
        board = lifeStep(board)
    startBoard = board.copy()
    delta = numpy.random.randint(1,5+1)
    for i in xrange(delta):
        board = lifeStep(board)
    stopBoard = board.copy()
    if stopBoard.any():   # non-empty board
        return (delta, startBoard, stopBoard)
    else:
        # print "ZERO stopBoard. Trying again..."
        return randomStartStopBoards(sideLength) # try again 

def readBoards(nBoards, includeStartBoard=False):
   for row_id in xrange(1, nBoards+1):
        delta, startBoard, stopBoard = randomStartStopBoards()
        if includeStartBoard:
            yield (row_id, delta, startBoard, stopBoard)
        else:
            yield (row_id, delta, stopBoard)

def readTestBoards(nBoards):
    # iterator returning: id, delta, stopBoard
    return readBoards(nBoards, includeStartBoard=False)

def readTrainBoards(nBoards):
    # iterator returning: id, delta, startBoard, stopBoard
    return readBoards(nBoards, includeStartBoard=True)

def print_board(board):
    for row in board:
        print ' '.join(['X' if col else '-' for col in row])

def do_tests():
    for rid, delta, start_board, stop_board  in readTrainBoards(100):
        print "\n***", "id:", rid, "delta:", delta,"***\n"
        print "START BOARD"
        print_board(start_board)
        print "STOP BOARD"
        print_board(stop_board)
        print '\n'

if __name__ == '__main__':
    do_tests()
