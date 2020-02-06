import EngineBSVD

numFeatures = 3
regularization = 0.05
minDeltaLL = 0.00
minIterations = 10
maxIterations = 100
fVoutInitConst = 0.1
fVinInitConst  = 0.1

ebsvd = EngineBSVD()
ebsvd.go(   numFeatures, regularization, \
            minDeltaLL, minIterations, maxIterations,\
            fVoutInitConst, fVinInitConst\
        )

