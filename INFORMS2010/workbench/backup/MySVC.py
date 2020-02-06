import scikits.learn.svm

class MySVC: 
# wrapper class to invert the returned result to predict prob(1), not prob(0) 
    def __init__(self, **kwargs):
        self._SVC = scikits.learn.svm.SVC(**kwargs)
    def fit(self,X,Y):
        self._SVC.fit(X,Y)
    def predict_proba(self,X):
        return 1.0 - self._SVC.predict_proba(X)   # maps 0->1, 1->0
