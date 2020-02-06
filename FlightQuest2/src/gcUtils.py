import math
from math import asin, sqrt, sin, cos, atan2

KM_PER_NAUTICALMILE = 1.852
KM_PER_MILE         = 1.60934

EARTH_RADIUS_KM     = 6371.0
EARTH_RADIUS_NM     = EARTH_RADIUS_KM / KM_PER_NAUTICALMILE
EARTH_RADIUS_M      = EARTH_RADIUS_KM / KM_PER_MILE


"""
From: http://williams.best.vwh.net/avform.htm#Intermediate

Distance between points

    The great circle distance d between two points with coordinates {lat1,lon1} and {lat2,lon2} is given by:
       d=acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon1-lon2))
    A mathematically equivalent formula, which is less subject to rounding error for short distances is:
       d=2*asin(sqrt((sin((lat1-lat2)/2))^2 + cos(lat1)*cos(lat2)*(sin((lon1-lon2)/2))^2))
"""

def gcDistRadians(pt1, pt2):
    lat1, lon1 = pt1
    lat2, lon2 = pt2
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2)) # degrees->radians
    d = 2.*asin(sqrt((sin((lat1-lat2)/2.))**2 + cos(lat1)*cos(lat2)*(sin((lon1-lon2)/2.))**2))
    return d

def gcDistKM(pt1, pt2):
    return gcDistRadians(pt1, pt2) * EARTH_RADIUS_KM

def gcDistNMile(pt1, pt2):
    return gcDistKM(pt1, pt2) / KM_PER_NAUTICALMILE

def gcDistMile(pt1, pt2):
    return gcDistKM(pt1, pt2) / KM_PER_MILE


"""
From: http://williams.best.vwh.net/avform.htm#Intermediate

Intermediate points on a great circle

    In previous sections we have found intermediate points on a great circle given either the crossing 
    latitude or longitude. Here we find points (lat,lon) a given fraction (f) of the distance (d) between them. 
    Suppose the starting point is (lat1,lon1) and the final point (lat2,lon2) and we want the point a 
    fraction f along the great circle route. f=0 is point 1. f=1 is point 2. The two points cannot 
    be antipodal ( i.e. lat1+lat2=0 and abs(lon1-lon2)=pi) because then the route is undefined. 
    The intermediate latitude and longitude is then given by [see code below for formulae]:
"""

def gcIntermediatePt(pt_begin, pt_end, f): 
    # f = fraction of great-circle distance (d) from pt1->pt2
    d = gcDistRadians(pt_begin, pt_end)
    lat1, lon1 = pt_begin
    lat2, lon2 = pt_end
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2)) # degrees->radians
    A = sin((1.-f)*d)/sin(d)
    B = sin(f*d)/sin(d)
    x = A*cos(lat1)*cos(lon1) +  B*cos(lat2)*cos(lon2)
    y = A*cos(lat1)*sin(lon1) +  B*cos(lat2)*sin(lon2)
    z = A*sin(lat1)           +  B*sin(lat2)
    lat=atan2(z,sqrt(x**2+y**2))
    lon=atan2(y,x)
    lat, lon = math.degrees(lat), math.degrees(lon)
    return (lat, lon)

def gcIntermediateFracs(pt_begin, pt_end, fracs, addStartEnd=False):
    # returns position(s) along arbitrary fractions of great-circle route between pt1->pt2
    pts = [ gcIntermediatePt(pt_begin, pt_end, frac) for frac in fracs]
    if addStartEnd:
        pts = [pt_begin] + pts + [pt_end]
    return pts

def intermediateFracs(npts):
    return ( (n+1.)/(npts+1) for n in xrange(npts) )

def gcIntermediate(pt_begin, pt_end, npts, addStartEnd=False):
    # returns evenly-spaced position(s) along great-circle route between pt1->pt2
    fracs = intermediateFracs(npts)
    return gcIntermediateFracs(pt_begin, pt_end, fracs, addStartEnd=addStartEnd)

# -----------------------------------------------------------------------------

# adapted from http://www.movable-type.co.uk/scripts/latlong.html
# Returns the (initial) bearing from this point to the supplied point, in degrees
# see http://williams.best.vwh.net/avform.htm#Crs for formulas 

def gcBearingRadiansToPt(pt_begin, pt_end):
    lat1, lon1 = pt_begin
    lat2, lon2 = pt_end
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2)) # degrees->radians
    dLon  = lon2 - lon1
    y = math.sin(dLon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
    brng = math.atan2(y, x)
    brng = math.degrees(brng)+360 % 360 
    return math.radians(brng) # initial bearing in degrees from North

# Returns the destination point from this point having travelled the given distance (in km) on the 
# given initial bearing (bearing may vary before destination is reached)
#   see http://williams.best.vwh.net/avform.htm#LL

def gcDestinationPt(pt_begin, brng, dist, earth_radius):
    # point on great circle path that's dist away from starting point at bearing brng
    # note: dist and earth_radius assumed to have the same units
    # also, brng is assumed to be the initial bearing in _radians_
    dist = dist / earth_radius # convert to radians (cancels length units)
    lat1, lon1 = pt_begin 
    lat1, lon1 = map(math.radians, (lat1, lon1)) # degrees->radians

    lat2 = math.asin( math.sin(lat1)*math.cos(dist) + math.cos(lat1)*math.sin(dist)*math.cos(brng) )
    lon2 = lon1 + math.atan2(  math.sin(brng)*math.sin(dist)*math.cos(lat1), 
                               math.cos(dist)-math.sin(lat1)*math.sin(lat2) )
    lon2 = (lon2 + 3.*math.pi) % (2.*math.pi) - math.pi # normalise to -180..+180 degrees
    return ( math.degrees(lat2), math.degrees(lon2) ) # return destination point

def gcPtAtDistance(pt_begin, pt_end, dist, earth_radius):
    # Find point at a specific distance from pt1 along a great-circle path defined by pt1->pt2
    brng = gcBearingRadiansToPt(pt_begin, pt_end)
    return gcDestinationPt(pt_begin, brng, dist, earth_radius)


# ------------------------------------------------------------------------

def _lineprint(tag, iterable):
        print tag
        for i in iterable:
            print '',i

def _tests():
    print "\nRunning tests\n"
    pt1 = (42.0, -74.5)
    pt2 = (30.5, -105.2)
    _lineprint("Start/End Points:", (pt1, pt2))
    print "gcDistRadians result:", gcDistRadians(pt1, pt2)
    print "gcDistKM      result:",    gcDistKM(pt1, pt2)
    print "gcDistNMile   result:",    gcDistNMile(pt1, pt2)
    print "gcDistMile    result:",    gcDistMile(pt1, pt2)
    _lineprint("gcIntermediatePt (halfway):", (gcIntermediatePt(pt1, pt2, 0.5)))
    _lineprint("gcIntermediate, 3 intermediate pts:", gcIntermediate(pt1, pt2, npts=3, addStartEnd=True))
    print "\nCorresponding R gcIntermediate output was:"
    print """
    > gcIntermediate(c(-74.5, 42.0), c(-105.2, 30.5), 3, addStartEnd=TRUE)
                        lon      lat
            [1,]  -74.50000 42.00000
            [2,]  -83.04147 39.91412
            [3,]  -91.01109 37.24204
            [4,]  -98.38748 34.07476
            [5,] -105.20000 30.50000
            > 
    """
    print "bearing(deg) from pt1->pt2: ", math.degrees(gcBearingRadiansToPt(pt1, pt2))

if __name__ == '__main__':
    _tests()

