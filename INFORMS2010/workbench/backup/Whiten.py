import scikits.learn.glm
import numpy

class Whiten:

    def __init__(self, C=1.0, whiteC=None, classifier=None):
        self.reg = C
        self.classifier = classifier(C)
        self.whiteReg = whiteC
        self.whiteClassifier = classifier(whiteC)

    def lag(self, X, shift= -1 ):
        if shift > 0:             # move future values into the past
            shiftedX = X[shift:]  # drop FIRST shift rows/values 
            padding = numpy.array( [shiftedX[-1]] * abs(shift) ) # pad RIGHT with LAST row/value
            return numpy.concatenate((shiftedX,padding)) 
        elif shift < 0:           # move past values into the future 
            shiftedX = X[:shift]  # drop LAST shift rows/values (shift is negative)
            padding = numpy.array( [shiftedX[ 0]] * abs(shift) ) # pad LEFT with FIRST row/value
            return numpy.concatenate((padding, shiftedX))
        else:
            return X

    def calcRho(self, residuals):
        rho = numpy.dot(residuals, self.lag(residuals)) / \
              numpy.dot(residuals,          residuals ) 
        return rho

    def fit(self, X, Y):
        self.classifier.fit(X,Y)
        residuals = Y - self.classifier.predict(X)
        self.rho = self.calcRho(residuals)
        # print "Rho before whitening:", self.rho, 
        Xprime = ( X - self.rho*self.lag(X) )
        Yprime = ( Y - self.rho*self.lag(Y) )
        self.whiteClassifier.fit(Xprime, Yprime)  
        #residuals2 = Yprime - self.classifier.predict(Xprime)
        #print "  After whitening:", self.calcRho(residuals2) 
        self.coef_ = self.whiteClassifier.coef_

    def predict(self, X):
        Xprime = ( X - self.rho*self.lag(X) )
        Yprime = self.whiteClassifier.predict(Xprime)
        Y = [0]
        for Yp in Yprime:
            Y.append( Yp + self.rho*Y[-1] )  # integrates Yprime (partially, depending on rho) 
        Y = numpy.array( Y[1:] ) 
        return Y

