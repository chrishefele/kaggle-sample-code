import scipy.interpolate
import numpy, numpy.random

N = 5

x = numpy.arange(0,N)
y = numpy.random.random((N,2)).transpose()

print x
print y.transpose()

f = scipy.interpolate.interp1d(x,y, bounds_error=False, assume_sorted=False)

xnew = numpy.arange(0, 2.25, 0.25)
ynew = f(xnew)

print xnew.transpose()
print ynew.transpose()


# cv2.HuMoments(cv2.moments(image)).flatten()

