from scipy.signal import convolve2d
import numpy 
import itertools

SIDE_LENGTHS = range(1, 21)  # board size, 1x1 to 20x20
SAMPLE_IDS    = xrange(10000) # number of random boards to try 
STEP_LIMIT    = 10000    # when to quit if didn't reach attractor

COMMA = ','
KERNEL = numpy.ones((3,3))

def lifeStep(board):
    nbrs_count = convolve2d(board, KERNEL, mode='same', fillvalue=0) - board
    return (nbrs_count==3) | (board & (nbrs_count==2))

"""
def boardString(board):  
    rowStrings = []
    for row in board:
        rowStrings.append(''.join(['X' if col else 'o' for col in row]))
    return '_'.join(rowStrings)
"""

def randomInitBoard(sideLength):
    fillFraction = numpy.random.uniform(low=0.01, high=0.99, size=1)
    board = numpy.random.binomial(n=1, p=fillFraction, size=(sideLength, sideLength)) 
    return board == 1

def stepsToAttractor(sideLen, stepLimit):
    board = randomInitBoard(sideLen)
    pastBoards = set()
    steps = 0
    boardStr = board.tostring()
    while boardStr not in pastBoards and steps < stepLimit:
        pastBoards.add(boardStr)
        board = lifeStep(board)
        boardStr = board.tostring()
        steps += 1
    return steps

def main():
    print "side, steps"
    for side in SIDE_LENGTHS:
        for sample_id in SAMPLE_IDS:
            steps = stepsToAttractor(side, STEP_LIMIT)
            print side, COMMA, steps
            
main()


