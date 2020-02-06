import pandas
import numpy as np

TEST_FILE  = '../../download/test.csv'
TRAIN_FILE = '../../download/train.csv'

BOARD_ROWS  = 20
BOARD_COLS  = 20
BOARD_SHAPE = (BOARD_ROWS, BOARD_COLS)
BOARD_CELLS = BOARD_ROWS * BOARD_COLS

def colNames(tag): 
    return [ tag+'.{col}'.format(col=col) for col in xrange(1,BOARD_CELLS+1)]

def hashFromRowCols(row, cols):
        return hash(tuple(np.array(row[cols])))
    
def readBoards(filename, includeStartBoard=False):
    df = pandas.read_csv(filename)
    nrows, ncols = df.shape
    rows = (df.irow(r) for r in xrange(nrows))
    for row in rows:
        if includeStartBoard:
            startHash = hashFromRowCols(row, colNames('start'))
            stopHash  = hashFromRowCols(row, colNames('stop' )) 
            yield (row['id'], row['delta'], startHash, stopHash)
        else:
            stopHash  = hashFromRowCols(row, colNames('stop' )) 
            yield (row['id'], row['delta'], stopHash)

def main():
    stop_hashes = set()
    for rid, delta, start_hash, stop_hash in readBoards(TRAIN_FILE, includeStartBoard=True):
        # print 'id',rid, 'delta',delta,'start_hash', start_hash, 'stop_hash', stop_hash
        if rid % 100 == 0:
            print rid,
        if stop_hash in stop_hashes:
            print "DUPLICATE board? -> stop hash duplicate:", stop_hash
        else:
            pass
            #stop_hashes.add(stop_hash)

main()
