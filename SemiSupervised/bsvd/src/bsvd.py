# usage: jython bsvd.py <regularization> <train_features_outfile> <test_features_outfile>

import sys
import EngineBSVD

assert len(sys.argv) == 4 # script name + 3 args above

regularization  = float(sys.argv[1]) # 0.02 seems best
print "Regularization to use:", regularization

numFeatures     = 56       # number of binary features
minDeltaLL      = 0.0001
minIterations   = 10
maxIterations   = 200
fVoutInitConst  = 0.1
fVinInitConst   = 0.1

ebsvd = EngineBSVD()

ebsvd.FILE_FEATURES_TRAIN = sys.argv[2]
ebsvd.FILE_FEATURES_TEST  = sys.argv[3]

ebsvd.go(   numFeatures, regularization, \
            minDeltaLL, minIterations, maxIterations,\
            fVoutInitConst, fVinInitConst\
        )

