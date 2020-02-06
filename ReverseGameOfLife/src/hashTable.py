# hashTable - implemented here because it's more memory efficient than a dict
#
# NOTE: Best to have more slots than expected items; 5% hash collision when 10% full. 

import numpy
import hashlib

TYPE_INT = type(int())

class hashTable:

    def __init__(self, nrow, ncol, dtype=int):
        self.nrow = nrow
        self.ncol = ncol
        self.table = numpy.zeros((nrow, ncol), dtype=dtype)

    def __getitem__(self, row_key):
        # index directly into the table using an int
        # otherwise, the sha1 hash of a keystring maps into the table
        if type(row_key) == TYPE_INT:
            row_index = row_key % self.nrow
        else:
            row_index   = int(hashlib.sha1(row_key).hexdigest(), 16) % self.nrow
        return self.table[row_index]

    def __iter__(self):
        # somewhat duplicates the behavior of dicts, returning ints which 
        # can be used to index into the table for hashed values seen 
        for row_id, row in enumerate(self.table):
            if sum(row) > 0:
                yield row_id

    def printtable(self):
        print self.table

def do_tests():
    ht = hashTable(5,2)
    ht.printtable()
    print [ht[r] for r in ht]

    ht['hello'][0] = 42
    ht.printtable()
    print [ht[r] for r in ht]

    ht['hello'][1] += 99
    ht.printtable()
    print [ht[r] for r in ht]

    ht['python'][1] = 8675309
    ht.printtable()
    print [ht[r] for r in ht]

if __name__ == '__main__':
    do_tests()
