# cellModels.py - use stop cells (or stop cell evolution) to predict cell start state

from readBoards import readTrainBoards, readTestBoards, BOARD_CELLS
import lifeStep
import collections
import numpy
import sys
import csv 
import math
import pickle
from sklearn.cross_validation import KFold
from collections import namedtuple
import syntheticBoards # for readTranBoards

GENERATIONS         = 9  # for cell evolution model, 9=optimum found via testing 
NEIGHBOR_RADII      = (1,2,2,2,3,3) # per-delta optimum radii found for neighbor model 

FOLDS               = 2 
MAX_DELTA           = 5

USE_DIHEDRAL_CACHE              = False # 2x faster, but memory hungry
TEST_MODE                       = False # use a small sample of data for speed
STRONG_PATTERN_PRINT_THRESHOLD  = 100   # suppresses weak/infrequent patterns 
PRINT_ROW_STATUS_MOD            = 100

# Regularization section
REGULARIZATIONS = (-1,0,1,2,3,4,5,6,7,8,9,10,20,50,100,1000,10000,100000,1000000)

# Optimum regularizations below found via testing (examining the training error report)
# >>for evolution models, delta:regularization
REG_LOW = {1:0,  2:20,   3:20,    4:20,    5:20   }  # at error minimum
REG_MED = {1:5,  2:100,  3:500,   4:500,   5:500  }  # at start of reg impact
REG_HIGH= {1:20, 2:1000, 3:10000, 4:10000, 5:10000}  # +0.0004 err above optimum 

# >>for neighbor models, delta:regularization, opt for neighbors models, 250K boards
#REG_NBRS= {1:0,  2:1,    3:3,     4:2,     5:2    }  
# >>for neighbor models, delta:regularization, using all radius 2 models & 4M training boards
REG_NBRS= {1:0,  2:2,    3:4,     4:6,     5:6    }  

# select appropriate regularization for the model being used
OPT_REG_VS_DELTA = REG_NBRS


def zeroDeadAliveCounts(): 
    return [0,0] 

class boardCellPatternModel:
    # Generic class; inherit from this when trying to capture 
    # different cell patterns, but overload boardCellPattern to define the pattern

    def __init__(self, maxPatterns=0): 
        # counters for cell patterns
        self.maxPatterns = maxPatterns
        self.clearTraining()

    def clearTraining(self):
        # self.trainCounts = collections.defaultdict(lambda: [0,0])  # lambda won't pickle
        self.trainCounts   = collections.defaultdict(zeroDeadAliveCounts)  # lambda won't pickle

    def boardCellPattern(self, board):
        # This is an Abstract method; must override this when inheriting from this 
        # class to define the cell patterns that will be used for pattern matching
        # e.g. (cell evolution over timesteps, or neighbor cells)
        raise NotImplementedError, \
        "Must override boardCellPattern method when inheriting from boardCellPatternModel class"

    def cellValuesToStr(self, cells):
        #return ''.join(('X' if cell else '-' for cell in cells))
        # hex string representation of cell states (interpreted as bits); chops leading 0x prefix
        return hex(int(''.join(['1' if c else '0' for c in cells]), 2))[2:]

    def addTrainingExample(self, startBoard, stopBoard):
        if self.maxPatterns and (len(self.trainCounts) > self.maxPatterns):
            return
        nrow, ncol = stopBoard.shape 
        boards = self.boardCellPattern(stopBoard)
        for col in xrange(ncol):
            for row in xrange(nrow):
                cell_values = self.cellValuesToStr( boards[:,row,col] )
                cell_start = 1*startBoard[row,col]  # converts boolean to 0/1
                self.trainCounts[cell_values][cell_start] += 1

    def predictBoardCounts(self, stopBoard):
        nrow, ncol = stopBoard.shape 
        deadCountBoard  = numpy.zeros((nrow,ncol), dtype=int) 
        aliveCountBoard = numpy.zeros((nrow,ncol), dtype=int) 
        boards = self.boardCellPattern(stopBoard)
        for col in xrange(ncol):
            for row in xrange(nrow):
                cell_values = self.cellValuesToStr(boards[:,row,col])
                deadCount, aliveCount = self.trainCounts.get(cell_values, (0,0))
                deadCountBoard[row,col]  = deadCount
                aliveCountBoard[row,col] = aliveCount
        return deadCountBoard, aliveCountBoard

    def predictBoard(self, stopBoard, regularization):
        deadCounts, aliveCounts = self.predictBoardCounts(stopBoard)
        return aliveCounts > (deadCounts + regularization)

    def predictBoardError(self, startBoard, stopBoard, regularization, perCell=False):
        predBoard = self.predictBoard(stopBoard, regularization)
        if perCell:
            return 1*(startBoard != predBoard)
        else:
            return sum(sum(startBoard != predBoard))
                
    def predictBoardErrorVsRegs(self, startBoard, stopBoard, regularizations, perCell=False):
        deadCounts, aliveCounts = self.predictBoardCounts(stopBoard)
        errVsReg = {}
        for reg in regularizations:
            predBoard = aliveCounts > (deadCounts + reg)
            if perCell:
                err = 1*(startBoard != predBoard)
            else:
                err = sum(sum(startBoard != predBoard))
            errVsReg[reg] = err
        return errVsReg

    def printCounts(self):
        if not self.trainCounts: 
            return
        print "Number of unique cell patterns found:", len(self.trainCounts),"\n"
        strong_pattern_stats = []
        for cell_values in self.trainCounts:
            nDead, nAlive = self.trainCounts[cell_values]
            pattern_stats = (nAlive-nDead, nAlive+nDead, nDead, nAlive, cell_values)
            if abs(nAlive-nDead) > STRONG_PATTERN_PRINT_THRESHOLD:
                # print just the strong patterns (above threshold)
                strong_pattern_stats.append(pattern_stats)
        strong_pattern_stats.sort()

        for pattern_stats in strong_pattern_stats:
            print '(1-0: %-10i  1+0: %-10i) (0: %-10i 1: %-10i)  %s' % pattern_stats

class boardCellEvolutionModel(boardCellPatternModel):

    def __init__(self, generations, maxPatterns=0):
        # counters for cell evolution patterns
        self.generations = generations
        self.maxPatterns = maxPatterns
        self.clearTraining()

    def boardCellPattern(self, board):
        # evolve each cell N Game-of-Life generations from the stop board 
        # and return a stack of these boards. A slice through the stack
        # yields a given cell's evolution for N generations forward 
        boards = []
        for g in xrange(self.generations):
            boards.append(board)
            board = lifeStep.lifeStep(board)
        boards = numpy.array(boards)
        return boards


class boardCellNeighborsModel(boardCellPatternModel):

    def __init__(self, radius, maxPatterns=0):
        # counters for cell patterns
        self.clearTraining()
        self.maxPatterns = maxPatterns
        self.radius = abs(radius)
        self.dradii = tuple(range(-radius, radius+1))
        self.dihedral_cache = {}

    def flatCellsToStr(self, cells): 
        # return ''.join(('X' if cell else '-' for cell in cells))
        return hex(int(''.join(['1' if c else '0' for c in cells]), 2))[2:]

    def cellValuesToStr(self, cells):
        # overloaded here to capture dihedral groups of square cell patterns
        # (rotations & mirror images of a pattern map to the same result)
        assert cells.ndim == 1
        cells_str = self.flatCellsToStr(cells)
        if cells_str in self.dihedral_cache:
            return self.dihedral_cache[cells_str]

        n = int(math.sqrt(len(cells)))
        cellsSquared = cells.reshape((n,n))
        cellsFlipped = numpy.fliplr(cellsSquared)
        dihedral_group = [numpy.rot90(cellsSquared,k=k) for k in (0,1,2,3)] + \
                         [numpy.rot90(cellsFlipped,k=k) for k in (0,1,2,3)]
        dihedral_str   = min([self.flatCellsToStr(e.flatten()) for e in dihedral_group])
        if USE_DIHEDRAL_CACHE:
            self.dihedral_cache[cells_str] = dihedral_str
        return dihedral_str

    def boardCellPattern(self, board):
        # Create a stack of shifted versions of the stop board such that 
        # each shifted board has one of the original cell's neighbors  in the 
        # same position as the original cell.  This allows slices throught the stack 
        # of boards to yield the neighbor cells for any cell position on the board.
        nrows, ncols = board.shape
        radius = self.radius
        # Off-board neighbors assumed to be zero, so zero-pad the borders by embedding 
        # the original board in the center of a larger zero'd board 
        board0 = numpy.zeros( (nrows+2*radius, ncols+2*radius), dtype=bool)
        board0[radius:-radius, radius:-radius] = board 
        # now create a stack of position-shifted boards
        neighbor_boards = []
        for drow in self.dradii:
            for dcol in self.dradii:
                row_start, row_end  = radius + drow, radius + drow + nrows
                col_start, col_end  = radius + dcol, radius + dcol + ncols
                neighbor_board = board0[ row_start:row_end, col_start:col_end ] 
                neighbor_boards.append(neighbor_board)
        return numpy.array(neighbor_boards)


# ---- start of support functions for trainingMain below

def printRowStatus(r):
    if r % PRINT_ROW_STATUS_MOD == 0:
        print r, 
        sys.stdout.flush()
 
def printModelCounts(models):
    print 'Model patterns are:'
    for delta, model in enumerate(models):
        print "\n***Delta = ", delta
        model.printCounts() 
    print

def printModelNumUniquePatterns(row_id, models):
    if row_id % PRINT_ROW_STATUS_MOD == 0:
        print 'row:', row_id, 'delta_nuniques:',
        for delta, model in enumerate(models):
            if model.trainCounts:
                print delta, len(model.trainCounts),
        print

def printErrorReport(exampleBoard, err_count, board_count):
    # Error reporting, broken down by delta, generations, regularization
    print '\n*** ERROR REPORT ***\n'
    board_rows, board_cols = exampleBoard.shape
    cells_per_board = board_rows * board_cols
    for errorCase in sorted(err_count):
        print 'delta %2i reg %7i' % errorCase,
        print 'errs %8i'     % err_count[errorCase], 
        print 'boards %8i'   % board_count[errorCase],
        frac = 1.*err_count[errorCase] / (board_count[errorCase]*cells_per_board)
        print 'meanCellError %8.5f' % frac
    # TODO add overall error, given regularizations for each delta?

def printCellErrorReport(cellerr_count, board_count):
    # Error reporting, broken down by delta, regularization, row/col position 
    print '\n*** CELL ERROR REPORT ***\n'
    print 'cellerr, delta, reg, row, col, cellerr'
    for errorCase in sorted(cellerr_count):
        delta, reg = errorCase
        cellerrs = 1.*cellerr_count[errorCase] / board_count[errorCase]
        for row_id, row in enumerate(cellerrs):
            for col_id, cellerr in enumerate(row):
                print 'cellerr, %2i, %7i, %2i, %2i, %8.5f' % (delta, reg, row_id, col_id, cellerr)
    print

def myKFold(n, n_folds=2):
    # Returns train & test set boolean masks for KFold cross validation
    # Unlike KFold, myKFold handles n_folds=1, which is useful for test-set training
    if n_folds >= 2:
        return KFold(n, n_folds=n_folds, indices=False)
    elif n_folds == 1:
        allMask = numpy.ones(n, dtype=bool)
        return (masks for masks in ((allMask,allMask),))
    else:
        raise ValueError, 'Number of cross-validation folds must be >0'

# ---- end of support routines for trainingMain below

def preTrainModels(models, nBoards):
    print '\nPre-Training models using',nBoards,'synthetic boards'
    #for model in models:
    #    model.clearTraining()
    for row_id, delta, startBoard, stopBoard in syntheticBoards.readTrainBoards(nBoards):
        # printRowStatus(row_id)
        printModelNumUniquePatterns(row_id, models)
        models[delta].addTrainingExample(startBoard, stopBoard)
    print '\nFinished Pre-Training models' 
    printModelCounts(models)  
    return models 

def CVtrainModels(models, n_folds=FOLDS, modelsPreTrained=False):
    # note: models = a list of predictive model objects, one for each delta
    print 'Reading training data'
    trainData = numpy.array( list(readTrainBoards()), dtype=object)
    if TEST_MODE:
        trainData = trainData[1:500] # use a sample for speed
    print 'Done reading training data'

    # setup error tracking data structures
    ErrorCase = namedtuple('ErrorCase','delta reg')
    err_count     = collections.defaultdict(int)
    board_count   = collections.defaultdict(int)
    cellerr_count = collections.defaultdict(int)

    # do k-fold cross validation while training 
    kf = myKFold(len(trainData), n_folds=n_folds)
    for fold_num, (trainMask, testMask) in enumerate(kf):

        if not modelsPreTrained: 
            print '\nTraining for fold', fold_num, 'using', sum(trainMask), 'rows\n'
            for model in models:
                model.clearTraining()
            for row_id, delta, startBoard, stopBoard in trainData[trainMask]:
                printRowStatus(row_id)
                models[delta].addTrainingExample(startBoard, stopBoard)
            print '\nFinished training for fold', fold_num

        printModelCounts(models)  

        print '\nMaking CV error estimates for fold', fold_num, 'using', sum(testMask),'rows\n'
        for row_id, delta, startBoard, stopBoard in trainData[testMask]:
            printRowStatus(row_id)
            # tabulate error vs regularization 
            errVsReg = models[delta].predictBoardErrorVsRegs(startBoard, stopBoard, REGULARIZATIONS)
            cellerrVsReg = models[delta].predictBoardErrorVsRegs(startBoard, stopBoard, REGULARIZATIONS, perCell=True)
            for reg in errVsReg:
                errorCase = ErrorCase(delta, reg)
                err_count[    errorCase] += errVsReg[reg]
                cellerr_count[errorCase] += cellerrVsReg[reg]
                board_count[  errorCase] += 1 
        print '\nFinished making CV error estimates for fold', fold_num

    # print total error accumulated across all folds
    printErrorReport(stopBoard, err_count, board_count)  
    printCellErrorReport(cellerr_count, board_count)  
    return models


class SubmissionFile:
    def __init__(self, fname):
        self.cellNames = tuple('start.%i' % i for i in xrange(1,BOARD_CELLS+1))
        colNames = ('id',) + self.cellNames
        self.foutCSV = csv.DictWriter(open(fname,'w'), fieldnames=colNames)
        self.foutCSV.writerow( {cn:cn for cn in colNames} ) # write header
        
    def writeBoard(self, row_id, board):
        nrow, ncol = board.shape
        ncells = nrow*ncol
        cellVals = 1*board.reshape(ncells, order='F') # convert back from column major order
        rowDict = { cn:cv for cn,cv in zip(self.cellNames, cellVals) }
        rowDict['id'] = row_id
        self.foutCSV.writerow(rowDict)

def printRegularization(regVsDelta):
    print "\nRegularization values for predictions"
    for delta in regVsDelta:
        print '  delta: %i --> regularization %i' % (delta, regVsDelta[delta])
    print

def saveModels(models, filename):
    print "writing models to:", filename
    fout = open(filename, 'wb')
    pickle.dump(models, fout)
    fout.close()
    print "finished writing models to:", filename

def loadModels(filename):
    print "reading models from:", filename
    fin = open(filename, 'rb')
    models = pickle.load(fin)
    fin.close()
    print "finished reading models from:", filename
    return models

def makeSubmission(models, fname):
    print '\nReading test data for submission\n'
    testData = numpy.array( list(readTestBoards()), dtype=object)
    print '\nFinished reading test data for submission'
    printRegularization(OPT_REG_VS_DELTA) 
    print '\nMaking submission predictions\n'
    subFile = SubmissionFile(fname)
    for row_id, delta, stopBoard in testData:
        printRowStatus(row_id)
        regularization = OPT_REG_VS_DELTA[delta] 
        predBoard = models[delta].predictBoard(stopBoard, regularization)
        subFile.writeBoard(row_id, predBoard)
    print '\nWrote submission to:', fname,'\n'


