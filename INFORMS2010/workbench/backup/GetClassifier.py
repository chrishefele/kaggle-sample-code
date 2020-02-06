import scikits.learn.logistic
import scikits.learn.glm
from MySVC import MySVC
from Whiten import Whiten
import scikits.learn.svm
from Cointegration import Cointegration


def getClassifier(classifierName, gamma = None):
    functionLookup = {     \
    'logregL1' : (lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l1')),\
    'logregL2' : (lambda reg: scikits.learn.logistic.LogisticRegression(C=reg, penalty='l2')),\
    'linregL1' : (lambda reg: scikits.learn.glm.Lasso(alpha=reg)),\
    'linregL2' : (lambda reg: scikits.learn.glm.Ridge(alpha=reg)),\
    'svmlin'   : (lambda reg: MySVC(C=reg, kernel='linear', probability=True)),\
    'svmrbf'   : (lambda reg: MySVC(C=reg, kernel='rbf', gamma=gamma, probability=True)),\
    'svrlin'   : (lambda reg: scikits.learn.svm.SVR(C=reg, kernel='linear', probability=False)),\
    'svrrbf'   : (lambda reg: scikits.learn.svm.SVR(C=reg, kernel='rbf', \
                                                    gamma=gamma, probability=False)),\
    'cointL1'  : (lambda reg: Cointegration(C=reg, penalty='l1')), \
    'cointL2'  : (lambda reg: Cointegration(C=reg, penalty='l2')), \
    'wlinregL1': (lambda reg: Whiten(C=reg, whiteC=reg, \
                              classifier=getClassifier(classifierName='linregL1'))), \
    'wlinregL2': (lambda reg: Whiten(C=reg, whiteC=reg, \
                              classifier=getClassifier(classifierName='linregL2')))  \
    }
    return functionLookup[ classifierName ] 

def getClassifierPredictProbsFlag(classifierName):
    if 'svr' in classifierName:
        return False
    else:
        return True

