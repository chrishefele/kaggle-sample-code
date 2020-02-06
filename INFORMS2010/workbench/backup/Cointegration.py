import scikits.learn.glm
import numpy

class Cointegration:

    def __init__(self, C=1.0, penalty='l2'):
        if penalty=='l2':
            self.classifier = scikits.learn.glm.Ridge(alpha=C)
        elif penalty=='l1':
            self.classifier = scikits.learn.glm.Lasso(alpha=C)
        else:
            raise ValueError("Cointegration penalty must be l1 or l2")

    def fit(self, X,Y):
        integratedY = numpy.cumsum(Y-Y.mean())
        ctrIntegratedY = integratedY - integratedY.mean()
        normCtrIntY = ctrIntegratedY / ctrIntegratedY.std()
        #
        integratedX = numpy.cumsum(X-numpy.mean(X, axis=0), axis=0)
        ctrIntegratedX = integratedX - numpy.mean(integratedX,axis=0)
        normCtrIntX = ctrIntegratedX / numpy.std(ctrIntegratedX,axis=0)
        #
        self.classifier.fit(normCtrIntX, normCtrIntY)
        self.coef_ = self.classifier.coef_

    def predict(self,X):
        integratedX = numpy.cumsum(X-numpy.mean(X, axis=0),  axis=0)
        ctrIntegratedX = integratedX - numpy.mean(integratedX,axis=0)
        normCtrIntX = ctrIntegratedX / numpy.std(ctrIntegratedX,axis=0)
        integratedPreds =  self.classifier.predict(normCtrIntX)
        preds = numpy.gradient(integratedPreds)
        preds -= preds.mean()
        preds /= preds.std()
        return preds

