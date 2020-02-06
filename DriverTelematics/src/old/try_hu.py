
from tripUtils import readTripFiles, tripHuMoments, tripInterpolate, tripContour
import numpy as np
import cv2, cv

def dot(a,b):
    return (a*b).sum()

def mag(a):
    return np.sqrt(dot(a,a))

def diffmag(a, adx):
    dx = (a-adx)
    return mag(dx) / mag(a)

a   = np.array([(1,1), (2,1),(3,2), (4,2), (5,2), (4,3)])
a_i = tripInterpolate(a, 20) 

b  = np.array([(1,0), (2,2),(3,0), (4,3), (5,0), (5,5)])

MATCH = cv.CV_CONTOURS_MATCH_I3

print "match of a & b:", cv2.matchShapes(tripContour(a), tripContour(b), method=MATCH, parameter=1.)
print "match of a & a:", cv2.matchShapes(tripContour(a), tripContour(a), method=MATCH, parameter=1.)

print "match of a & ai:", cv2.matchShapes(tripContour(a), tripContour(a_i), method=MATCH, parameter=1.)
print "match of b & ai:", cv2.matchShapes(tripContour(b), tripContour(a_i), method=MATCH, parameter=1.)


m_0 = tripHuMoments(a)
print tripHuMoments(a)
print tripHuMoments(b)


"""
for n in (2,4,8, 16, 24, 48, 96, 200, 400, 800):
    a_n = tripInterpolate(a, n) 
    m_n = tripHuMoments(a_n)
    print n, diffmag(m_0, m_n)
"""
