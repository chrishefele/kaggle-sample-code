# driver.py
#
# Runs classifier on the metrics, using default 
# paramaters for rough/quick AUC estimation
#
# usage: python driver.py <maxFeatures> <maxDepth> 
# or     python driver.py 
#
# 

import globalConst
from classifier import Classify
from sklearn.ensemble import GradientBoostingClassifier
import sys
import os.path

def useIfExists(fname):
    return fname if os.path.isfile(fname) else None

def main(maxFeatures=30, maxDepth=8):

    print "maxFeatures:", maxFeatures
    print "maxDepth   :", maxDepth

    baseDir = globalConst.BASE_DIR

    params = {'max_depth':maxDepth, 'subsample':0.5, 'verbose':2, 'random_state':0,
        'min_samples_split':20, 'min_samples_leaf':20, 'max_features':maxFeatures,
        'n_estimators': 500, 'learning_rate': 0.05}
        #'n_estimators': 12000, 'learning_rate': 0.002}
    clf = GradientBoostingClassifier(**params)  

    # NOTE: first pass, no orderFile; 2nd pass, use orderfiles 
    test = Classify(trainFile=baseDir+'workspace/trainMetrics.csv', 
                    orderFile=useIfExists(baseDir+'/moby/corr32.csv') ) 

    test.validate(clf=clf, 
                  nFolds=2, 
                  featureImportance=True, 
                  outFile=baseDir+'moby/trainPredictions.csv')

    test.testAndOutput(clf=clf,
                  testFile=baseDir+'workspace/testMetrics.csv',
                  orderFile=useIfExists(baseDir+'/moby/testCorr32.csv'),
                  outfile=baseDir+'moby/testPredictions.sub') # NOTE .sub, not .csv 


if __name__=="__main__":
    print "Running driver"
    if len(sys.argv) == 3:
        maxFeatures = int(sys.argv[1])
        maxDepth    = int(sys.argv[2])
        main( maxFeatures=maxFeatures, maxDepth=maxDepth ) 
    else:
        main()

