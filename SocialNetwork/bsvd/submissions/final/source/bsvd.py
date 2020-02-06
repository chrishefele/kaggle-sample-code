# usage: jython bsvd.py <regularization> <probe_pred_outfile> <test_pred_outfile> 

import sys
import EngineBSVD

assert len(sys.argv) == 4 # 3 args, plus script name

regularization  = float(sys.argv[1]) # 0.02 seems best
print "Regularization to use:", regularization

numFeatures     = 100    # for reg 0.02, uses 22 features 
minDeltaLL      = 0.0001
minIterations   = 10
maxIterations   = 200
fVoutInitConst  = 0.1
fVinInitConst   = 0.1

ebsvd = EngineBSVD()
ebsvd.PREDICTIONS_PROBE = sys.argv[2] #"bsvd_predictions_probe.csv";
ebsvd.PREDICTIONS_TEST  = sys.argv[3] #"bsvd_predictions_test.csv";
# ebsvd.LRATE_SCALEUP     = float(sys.argv[4]) # 1.2 

ebsvd.go(   numFeatures, regularization, \
            minDeltaLL, minIterations, maxIterations,\
            fVoutInitConst, fVinInitConst\
        )

