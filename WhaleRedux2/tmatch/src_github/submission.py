import globalConst
from classifier import Classify
from sklearn.ensemble import GradientBoostingClassifier
import numpy as np
import os.path

def useIfExists(fname):
    return fname if os.path.isfile(fname) else None

def main():
    print "Running classifier"

    #baseDir = '/home/nick/whale/'
    baseDir = globalConst.BASE_DIR

    params = {'max_depth':8, 'subsample':0.5, 'verbose':2, 'random_state':0,
            'min_samples_split':20, 'min_samples_leaf':20, 'max_features':30,
            'n_estimators': 12000, 'learning_rate': 0.002}  
    #       'n_estimators': 12   , 'learning_rate': 0.002} # fewer trees for testing

    clf = GradientBoostingClassifier(**params)

    # Generate a submission with corr32 and all metrics
    test = Classify(trainFile=baseDir+'workspace/trainMetrics.csv',
                    orderFile=useIfExists(baseDir+'moby/corr32.csv') )
    test.testAndOutput(clf=clf,
        testFile=baseDir+'workspace/testMetrics.csv',
        orderFile=useIfExists(baseDir+'moby/testCorr32.csv'),
        outfile='submit32.sub')
    
    # Generate a submission with corr64 and no time metrics
    # noTime = np.array(range(150) + range(385,448))
    test = Classify(trainFile=baseDir+'workspace/trainMetrics.csv',
                    orderFile=useIfExists(baseDir+'moby/corr64.csv'),
                    excludeColStr='Time_')
    #               useCols=noTime)
    test.testAndOutput(clf=clf,
        testFile=baseDir+'workspace/testMetrics.csv',
        orderFile=useIfExists(baseDir+'moby/testCorr64.csv'),
        outfile='submit64.sub')

    # Blend
    s32 = np.loadtxt('submit32.sub',delimiter=',')
    s64 = np.loadtxt('submit64.sub',delimiter=',')
    sub_ = 0.5*s32 + 0.5*s64
    np.savetxt('blend.sub',sub_,delimiter=',')

    print "Done"

if __name__=="__main__":
    main()
