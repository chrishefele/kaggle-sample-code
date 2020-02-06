import numpy as np
import nltk
import os, os.path
import pandas
import scipy.interpolate
import cv2

def tripTurnAngles(pts):
    """
    Argument "pts" is an [N x 2] array with N rows of (x,y) points
    Returns an [N-2] element array of angles (in degrees) between 
    successive line segements connecting the points.
    """
    vecs = np.diff(pts, axis=0) # vectors between successive points
    v1 = vecs[ :-1].transpose() # vector sequence v1 -> v2
    v2 = vecs[1:  ].transpose() 
    v1_dot_x = v1[0]  # project vectors onto x & y axes
    v1_dot_y = v1[1]
    v2_dot_x = v2[0] 
    v2_dot_y = v2[1]
    angles = np.arctan2(v2_dot_y, v2_dot_x) - np.arctan2(v1_dot_y, v1_dot_x) 
    return np.rad2deg(angles) # angle of v2 relative to v1

def tripLegLengths(pts):
    """
    Argument "pts" is an [N x 2] array with N rows of (x,y) points.
    Returns an [N-1] element array of distances between successive points.
    """
    vecs = np.diff(pts, axis=0) # vectors between successive points
    lengths = np.sqrt(np.sum(vecs*vecs, axis=1)) # sqrt(x^2+y^2) per row
    return lengths

def tripFracComplete(pts):
    lengths = tripLegLengths(pts)
    lengths = np.insert(lengths, 0, 0.) # prepend zero dist for first pt
    return np.cumsum(lengths / lengths.sum()) 

def tripInterpolate(pts, n_interp_pts):
    trip_frac = tripFracComplete(pts)
    y = pts.transpose()
    interp_func = scipy.interpolate.interp1d(trip_frac, y, assume_sorted=False)
    new_trip_frac = np.linspace(trip_frac.min(), trip_frac.max(),  num=n_interp_pts)
    return interp_func(new_trip_frac).transpose()

def tripSignature(pts):
    n_breadcrumbs = max(2, int(tripLegLengths(pts)))
    leg_lengths = np.sum(tripLegLengths(pts))
    leg_angles  = np.abs(tripTurnAngles(pts))
    pass
    # interpolated accumulated turn angles vs distance after intial RDP


"""
def tripContour(pts):
    # cv2 contour type is an array of arrays of pts. 
    return pts.reshape((-1,1,2)).astype(np.int32)

def tripHuMoments(pts):
    # pts = N x 2 array of points
    # returns a 7-element array of Hu moments
    # cv2_contour = np.array(pts) 
    return cv2.HuMoments(cv2.moments(tripContour(pts))).flatten()
"""    

def readTripFiles(driver_dir):
    if not os.path.isdir(driver_dir):
        raise RuntimeError, driver_dir + "is not a directory!"
    trips = {}
    for trip_file in os.listdir(driver_dir):
        trip_id = int(trip_file.split('.')[0])  # e.g. '42.csv' -> 42
        fcsv = driver_dir + '/' + trip_file
        trip = pandas.read_csv(fcsv)
        trips[trip_id] = np.column_stack((trip.x, trip.y))
    assert len(trips) == 200
    return trips

def writeTripFile(trip_M, fname):
    """
    trip_M = [N x 2] matrix of (x,y) pts (one per row)
    fname  = filename to write the trip data to
    """
    df = pandas.DataFrame(trip_M, columns=['x','y'])
    df.to_csv(fname, index=False)



def tests():
    test_pts = np.array( [[0,0], [1,1], [1.5,1.5], [2,1], [2,2], [3,3.5]] )
    print "points :\n", test_pts
    print "angles :", tripTurnAngles(test_pts)
    print "lengths:", tripLegLengths(test_pts)
    print 
    print "angle-bigrams :", nltk.ngrams( tripTurnAngles(test_pts), 2)
    print "length-bigrams:", nltk.ngrams( tripLegLengths(test_pts), 2)

if __name__ == '__main__':
    tests()
