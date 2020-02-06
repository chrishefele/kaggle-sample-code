from scipy.signal import convolve2d
import numpy 
import os
import time

KERNEL = numpy.ones((3,3))

def lifeStep(board):
    # Applies Conway's Game Of Life rule(s) for creating the next generation:
    #  If an alive cell has <2 alive neighbors, the cell dies (due to loneliness...)
    #  If an alive cell has >3 alive neighbors, the cell dies (due to overcrowding...)
    #  If an alive cell has 2 or 3 neighbors,   the cell continues to live 
    #  If a dead cell has 3 neighbors, the cell becomes alive, otherwise it remains dead
    # Note: this function accepts and returns a boolean matrix (not integers)
    # Matrix borders here are zero-padded. 
    nbrs_count = convolve2d(board, KERNEL, mode='same', fillvalue=0) - board
    return (nbrs_count==3) | (board & (nbrs_count==2))

def printBoard(board):
    for row in board:
        print ' '.join(['0' if col else '-' for col in row])

def testLife():
    board = numpy.random.random((20,20)) > 0.7
    for gen in xrange(100):
        os.system('clear')
        print "Generation:", gen, "#alive:", sum(sum(board))
        printBoard(board)
        board = lifeStep(board)
        time.sleep(1)

def speedTestLife():
    # get about 10000 generations/second
    print 'testing speed'
    t0 = time.time()
    for i in xrange(1000):
        start_board = numpy.random.random((20,20)) > 0.5
        brd = start_board
        for gen in xrange(100):
            brd = lifeStep(brd)
    dt = time.time() - t0 
    print dt,'sec'
    print 1000.*100./dt, "generations per second" 

def print_convolve2d(board):
    TEST_KERNEL = numpy.ones((13,13))
    result = convolve2d(board, TEST_KERNEL, mode='same', fillvalue=0) - board
    print result.shape
    print result

def test_convolve2d():
    start_board = numpy.ones((20,20),dtype=bool)
    print start_board
    print_convolve2d(start_board)

if __name__=='__main__':
    # test_convolve2d()
    # speedTestLife()
    testLife()

