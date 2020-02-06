import itertools
import numpy
import math
import time

def flatCellsToStr(cells):
    # return ''.join(('X' if cell else '-' for cell in cells))
    return hex(int(''.join(['1' if c else '0' for c in cells]), 2))[2:]

def cellValuesToStr(cells):
    # capture dihedral groups of square cell patterns
    # (rotations & mirror images of a pattern map to the same result)
    n = int(math.sqrt(len(cells)))
    cellsSquared = cells.reshape((n,n))
    cellsFlipped = numpy.fliplr(cellsSquared)
    dihedral_group = [numpy.rot90(cellsSquared,k=k) for k in (0,1,2,3)] + \
                     [numpy.rot90(cellsFlipped,k=k) for k in (0,1,2,3)]
    result = min([flatCellsToStr(e.flatten()) for e in dihedral_group])
    return result

t0 = time.time()
pattern_hashes = set()
for n, pattern in enumerate(itertools.product((False, True), repeat=25)):
    cells = numpy.array(pattern, dtype=bool)
    pattern_hash = cellValuesToStr(cells)
    pattern_hashes.add(pattern_hash)
    if n % 100000 == 0:
        print int(time.time()-t0), 'sec', '     total_patterns:', n+1, 
        print 'dihedral_uniques:', len(pattern_hashes), 'ratio:', 1.*len(pattern_hashes)/(n+1) 


