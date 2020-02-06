# waypoints.py  - routines to calculate waypoints from current position to airport. 

# Note: Variable naming conventions are:
#   position / posn = ( latitude(deg), longitude(deg), altitude(ft) )
#   point / pt      = ( distance_to_end(nm), altitude(ft) )

import gcUtils
import pandas

WAYPOINT_ARRIVAL_RADIUS = 0.1 # Nautical Miles

class FlightModel:
    def __init__(self,  ascentSlope,  
                        descentSlope, 
                        cruiseSlope, cruiseIntercept, 
                        airspeedSlope, airspeedIntercept):
        # Note: distance decreases as plane moves towards airport
        # thus ascent slope is negative, descent slope is positive
        self.ascentSlope    = -abs(ascentSlope) 
        self.descentSlope   = +abs(descentSlope)
        self.cruiseSlope    = cruiseSlope
        self.cruiseIntercept= cruiseIntercept # cruise altitude
        self.airspeedSlope  = airspeedSlope   # climb as plane burns off fuel 
        self.airspeedIntercept  = airspeedIntercept
        self.customDescentSlope = None

    def airspeed(self, altitude):
        return self.airspeedIntercept + self.airspeedSlope * altitude

    def _altitudeVsDistance(self, alt_begin, dist_begin, slope, dist): 
        return alt_begin + -slope*(dist_begin - dist)

    def ascentAlt(self, alt_begin, dist_begin, dist):   
        return self._altitudeVsDistance(alt_begin, dist_begin, self.ascentSlope, dist)

    def descentAlt(self, alt_begin, dist_begin, dist):
        return self._altitudeVsDistance(alt_begin, dist_begin, self.descentSlope, dist)

    def cruiseAlt(self, alt_begin, dist_begin, dist):   
        return self._altitudeVsDistance(alt_begin, dist_begin, self.cruiseSlope, dist) 

    def setCustomDescentSlope(self, slope):
        self.customDescentSlope = +abs(slope)

    def customDescentAlt(self, alt_begin, dist_begin, dist):
        return self._altitudeVsDistance(alt_begin, dist_begin, self.customDescentSlope, dist)


def lineLineIntersectionPt(slope1, intercept1, slope2, intercept2): 
    # find intersection point of 2 lines given their slopes & intercepts
    x_intersect = 1.*(intercept2-intercept1)/(slope1-slope2)
    y_intersect = slope1*x_intersect + intercept1
    return (x_intersect, y_intersect)

def intersectPosition(posn_begin, slope_begin, posn_end, slope_end):
    # finds intersection position of 2 lines in the GC path plane between 2 points 
    (lat_begin, lon_begin, alt_begin) = posn_begin
    (lat_end,   lon_end,   alt_end  ) = posn_end
    dist_begin_to_end = gcUtils.gcDistNMile( (lat_begin,lon_begin), (lat_end,lon_end) )
    intercept_begin = alt_begin - slope_begin * dist_begin_to_end   
    intercept_end   = alt_end   - slope_end   * 0.0 
    dist_intersect, alt_intersect = lineLineIntersectionPt(
                            slope_begin, intercept_begin, slope_end, intercept_end )
    dist_from_begin = dist_intersect
    dist_from_end = dist_begin_to_end - dist_from_begin
    lat_intersect, lon_intersect  = gcUtils.gcPtAtDistance( 
                                        (lat_begin,lon_begin), (lat_end,lon_end), 
                                        dist_from_end, gcUtils.EARTH_RADIUS_NM    )
    return (lat_intersect, lon_intersect, alt_intersect)


def moveAirplane(posn_begin, posn_end, npts, 
                 altVsDistModel, airspeedVsAltModel, altMinMax=None):  
    # create intermediate position waypoints between two other waypoints

    # print "moveAirplane:", posn_begin, "-->", posn_end
    (lat_begin, lon_begin, alt_begin) = posn_begin
    (lat_end,   lon_end,   alt_end  ) = posn_end
    dist_begin = gcUtils.gcDistNMile( (lat_begin,lon_begin), (lat_end,lon_end) )
    if dist_begin < WAYPOINT_ARRIVAL_RADIUS:
        return noWaypoints(posn_begin, posn_end, npts, flightModel=None)

    pts = gcUtils.gcIntermediate((lat_begin,lon_begin),(lat_end,lon_end), npts) 
    # tricky: zip(*pts) unzips intermediate points with format
    # [(lat1,lon1),(lat2,lon2),...] into (lat1, lat2...), (lon1, lon2...)
    lats, lons = zip(*pts) 

    dists = [ dist_begin*(1.-frac) for frac in gcUtils.intermediateFracs(npts) ] 
    alts  = [ altVsDistModel(alt_begin, dist_begin, d) for d in dists ] 
    if altMinMax:
        altMin, altMax = min(altMinMax), max(altMinMax)
        alts = [ max(altMin, min(altMax,alt)) for alt in alts] 
    airspeeds = [ airspeedVsAltModel(alt) for alt  in alts ]
    
    lats = tuple(lats) + (lat_end, )
    lons = tuple(lons) + (lon_end, )
    alts = tuple(alts) + (alt_end, )
    airspeeds = tuple(airspeeds) + (airspeedVsAltModel(alt_end), )

    waypoints = { 'LatitudeDegrees':lats, 'LongitudeDegrees':lons, 
                  'AltitudeFeet':alts,    'AirspeedKnots':airspeeds }
    return waypoints  


def descend(posn_begin, posn_end, npts, flightModel):
    (_, _, alt_begin), (_, _, alt_end) = posn_begin, posn_end
    #assert alt_begin >= alt_end, 'alt_begin %d <= alt_end %d' % (alt_begin, alt_end)
    return moveAirplane(posn_begin, posn_end, npts, 
                        flightModel.descentAlt, flightModel.airspeed,
                        altMinMax = (alt_end,alt_begin) )

def directDescend(posn_begin, posn_end, npts, flightModel):
    (lat_begin, lon_begin, alt_begin) = posn_begin
    (lat_end,   lon_end,   alt_end  ) = posn_end
    #assert alt_begin >= alt_end
    dist = gcUtils.gcDistNMile( (lat_begin,lon_begin), (lat_end,lon_end) )
    slope = (alt_begin - alt_end) / dist
    flightModel.setCustomDescentSlope(slope)
    return moveAirplane(posn_begin, posn_end, npts, 
                        flightModel.customDescentAlt, flightModel.airspeed,
                        altMinMax = (alt_end,alt_begin) )

def ascend(posn_begin, posn_end, npts, flightModel):
    (_, _, alt_begin), (_, _, alt_end) = posn_begin, posn_end
    #assert alt_begin <= alt_end, 'alt_begin %d >= alt_end %d' % (alt_begin, alt_end)
    return moveAirplane(posn_begin, posn_end, npts, 
                        flightModel.ascentAlt, flightModel.airspeed,
                        altMinMax = (alt_begin,alt_end) )

def cruise(posn_begin, posn_end, npts, flightModel):
    (_, _, alt_begin), (_, _, alt_end) = posn_begin, posn_end
    return moveAirplane(posn_begin, posn_end, npts, 
                        flightModel.cruiseAlt, flightModel.airspeed)

def noWaypoints(posn_begin, posn_end, npts, flightModel):
    no_waypoints = {  'LatitudeDegrees':(), 'LongitudeDegrees':(), 
                      'AltitudeFeet':(),    'AirspeedKnots':()  }
    return no_waypoints

def oneWaypoint(posn, airspeed):
    lat, lon, alt = posn
    waypoint = { 'LatitudeDegrees':(lat,), 'LongitudeDegrees':(lon,), 
                 'AltitudeFeet':(alt,),    'AirspeedKnots':(airspeed,)  }
    return waypoint

def concatWaypoints(wpts1, wpts2):
    return { k:(wpts1[k]+wpts2[k]) for k in wpts1 } 

def moveAirplaneTwice(posn_begin,   move1_func, move1_slope, 
                      posn_nextleg, move2_func, move2_slope, 
                      posn_end,     npts,       flightModel):  
    # Find the intersection point between two lines:
    #   1. Line through posn_begin     with slope move1_slope
    #   2. Line through posn_nextleg   with slope move2_slope
    # Note that we do NOT fly to or through posn_nextleg, it's ONLY used
    # to define a line so we can find the posn_turn intersection point.
    # The plane DOES fly through posn_turn; it's where the flight 
    # path changes (e.g. ascent to descent).
    posn_turn = intersectPosition(posn_begin, move1_slope, posn_nextleg, move2_slope) 
    wpts1 = move1_func(posn_begin, posn_turn, npts, flightModel)
    wpts2 = move2_func(posn_turn,  posn_end,  npts, flightModel)
    return concatWaypoints(wpts1, wpts2)
    # return { k:(wpts1[k]+wpts2[k]) for k in wpts1 } 

def descendDescend(posn_begin, posn_end, npts, flightModel):
    posn_nextleg = posn_end 
    return moveAirplaneTwice(posn_begin,    descend, -flightModel.descentSlope,
                             posn_nextleg,  descend, +flightModel.descentSlope,
                             posn_end,      npts,    flightModel)
    # note initial descent is *away* from airport, thus first slope sign is (-)

def ascendDescend(posn_begin, posn_end, npts, flightModel):
    posn_nextleg = posn_end 
    return moveAirplaneTwice(posn_begin,    ascend,  flightModel.ascentSlope,
                             posn_nextleg,  descend, flightModel.descentSlope,
                             posn_end,      npts,    flightModel)

def cruiseDescend(posn_begin, posn_end, npts, flightModel):
    posn_nextleg = posn_end 
    return moveAirplaneTwice(posn_begin,    cruise,  flightModel.cruiseSlope,
                             posn_nextleg,  descend, flightModel.descentSlope,
                             posn_end,      npts,    flightModel)
    
def positionCruiseEnd(posn_begin, posn_end, flightModel):
    # Returns the position directly above the airport (posn_end) if 
    # the plane cruised there from the current position (posn_begin)
    # at *cruise* altitude (not the current altitude)
    # Note: plane may climb slowly, reflecting optimal cruise altitude
    # varies as plane burns off fuel and gets lighter.
    # Why do we need this point? It's useful for defining a line (cruise path)
    # that intersects a ascent/descent line from the current position.
    # That intersection is where the plane should start cruising. 
    (lat_begin,   lon_begin,   alt_begin)   = posn_begin
    (lat_end,     lon_end,     alt_end  )   = posn_end
    dist_begin = gcUtils.gcDistNMile( (lat_begin,lon_begin), (lat_end,lon_end) )
    dist_end   = 0.0  # dist to endpoint is 0 when at endpoint
    alt_cruise = flightModel.cruiseIntercept
    alt_end    = flightModel.cruiseAlt(alt_cruise, dist_begin, dist_end)
    return (lat_end, lon_end, alt_end)

def descendCruiseDescend(posn_begin, posn_end, npts, flightModel):
    posn_nextleg = positionCruiseEnd(posn_begin, posn_end, flightModel)
    return moveAirplaneTwice(posn_begin,    descend,       flightModel.descentSlope,
                             posn_nextleg,  cruiseDescend, flightModel.cruiseSlope,
                             posn_end,      npts,          flightModel)

def ascendCruiseDescend(posn_begin, posn_end, npts, flightModel):
    posn_nextleg = positionCruiseEnd(posn_begin, posn_end, flightModel)
    return moveAirplaneTwice(posn_begin,    ascend,        flightModel.ascentSlope,
                             posn_nextleg,  cruiseDescend, flightModel.cruiseSlope,
                             posn_end,      npts,          flightModel)


def cruisePossible(posn_begin, posn_end, flightModel):
    # Is there enough distance to climb to cruise altitude before descending to the destination?
    cruise_alt = flightModel.cruiseIntercept
    lat, lon, alt = intersectPosition( posn_begin, flightModel.ascentSlope, 
                                       posn_end,   flightModel.descentSlope )
    if alt < cruise_alt:
        return False   # reached descent path before reaching cruise altitude
    else:
        return True

def classifyZone(posn_begin, posn_end, flightModel):
    # classify current position into one of 4 zones; useful for picking a flightpath 
    (lat_begin, lon_begin, alt_begin) = posn_begin
    (lat_end,   lon_end,   alt_end  ) = posn_end
    dist_to_end = gcUtils.gcDistNMile( (lat_begin,lon_begin), (lat_end,lon_end) )
    cruise_alt  = flightModel.cruiseIntercept
    direct_descent_slope= float(alt_begin - alt_end) / dist_to_end 

    if direct_descent_slope > abs(flightModel.descentSlope):
        return 'near-high'  # short-range, high-altitude (over/near airport)
    elif alt_begin > cruise_alt:
        return 'far-high'   # long-range,  high-altitude
    elif cruisePossible(posn_begin, posn_end, flightModel):
        return 'far-low'    # long-range,  low-altitude 
    else:
        return 'near-low'   # short-range, low-altitude (no cruise leg)


zoneNum = { 'near-high':0, 'near-low':1, 'far-low':2, 'far-high':3 }

zoneOptionFunctions = { 
    ('near-high',0) : noWaypoints, 
    ('near-high',1) : directDescend,
    ('near-high',2) : descendDescend, 
    ('near-high',3) : cruiseDescend,

    ('near-low', 0) : noWaypoints, 
    ('near-low', 1) : directDescend,
    ('near-low', 2) : cruiseDescend,
    ('near-low', 3) : ascendDescend, 

    ('far-low',  0) : noWaypoints,
    ('far-low',  1) : directDescend,
    ('far-low',  2) : cruiseDescend, 
    ('far-low',  3) : ascendCruiseDescend,

    ('far-high', 0) : noWaypoints, 
    ('far-high', 1) : directDescend, 
    ('far-high', 2) : cruiseDescend, 
    ('far-high', 3) : descendCruiseDescend }

# zoneOptions selects which function is used in each flight zone.
#  zoneOptions = tuple(a,b,c,d) where:
#  a = near-high function option [0..3]
#  b = near-low  function option [0..3]
#  c = far-low   function option [0..3]
#  d = far-high  function option [0..3]

def waypoints(posn_begin, posn_end, npts_per_leg, flightModel, zoneOptions):
    zone = classifyZone(posn_begin, posn_end, flightModel)
    option = zoneOptions[ zoneNum[zone] ] 
    waypoint_func = zoneOptionFunctions[ (zone,option) ]
    return waypoint_func(posn_begin, posn_end, npts_per_leg, flightModel)

# ---------------- test code below --------------------------

def test_getFlightModel():
    flightModel = FlightModel(  ascentSlope  = 12321 / 100., 
                                descentSlope = 12345/ 100.,
                                cruiseSlope = 0., 
                                cruiseIntercept = 25000., 
                                airspeedSlope = 300 / 35000., 
                                airspeedIntercept = 150.   ) 
    return flightModel

def test_waypoint_primitives():
    # test plane-moving flight primatives / waypoint generation
    posn_begin_10k  = (40,-100,10000)
    posn_begin_20k  = (40,-100,20000)
    posn_begin_25k  = (40,-100,25000)
    posn_begin_30k  = (40,-100,30000)
    posn_end_10k    = (50,-110,10000)
    posn_end_20k    = (50,-110,20000)
    posn_end_30k    = (50,-110,30000)

    flightModel = test_getFlightModel()

    def printResult(func, args):
        print "**********", func.__name__, "**********"
        print pandas.DataFrame(func(*args))
        print
        
    npts = 10 

    printResult( descend,(              posn_begin_30k, posn_end_10k, npts, flightModel))
    printResult( directDescend,(        posn_begin_30k, posn_end_10k, npts, flightModel))
    printResult( ascend,(               posn_begin_10k, posn_end_30k, npts, flightModel))
    printResult( cruise,(               posn_begin_20k, posn_end_20k, npts, flightModel))
    printResult( descendDescend,(       posn_begin_30k, posn_begin_10k, npts, flightModel))
    printResult( ascendDescend,(        posn_begin_30k, posn_end_10k, npts, flightModel))
    printResult( cruiseDescend,(        posn_begin_30k, posn_end_10k, npts, flightModel))
    printResult( descendCruiseDescend,( posn_begin_30k, posn_end_10k, npts, flightModel))
    printResult( ascendCruiseDescend,(  posn_begin_10k, posn_end_10k, npts, flightModel))

def test_cruisePossible():
    print "\nTesting cruisePossible"
    flightModel = test_getFlightModel()
    for ll in range(100,110+1):
        posn_begin = (40,-100, 18000)
        posn_end   = (40+ll-100,-ll,  1000)
        print "cruisePossible:", posn_begin, "-->", posn_end, "is:",
        print cruisePossible(posn_begin, posn_end, flightModel)

def test_classifyZone():
    print "\nTesting classifyZone"
    flightModel = test_getFlightModel()
    def shiftStartPoint(alt):
        for latLon in range(100,110+1):
            posn_begin = (40+latLon-100, -latLon, alt)
            posn_end   = (40, -100, 1000)
            print "classifyZone:", posn_begin, "-->", posn_end, "Zone:",
            print classifyZone(posn_begin, posn_end, flightModel)
    shiftStartPoint(15000)
    shiftStartPoint(30000)

def test_waypoints():
    print "\nTesting waypoints"
    flightModel = test_getFlightModel()
    zoneOptions = (3,3,3,3)
    npts_per_leg = 10 
    posn_begin = (40, -100, 10000)
    for lon in range(100, 110):
        posn_end = (40.01, -lon, 0)
        print classifyZone(posn_begin, posn_end, flightModel),
        print posn_begin, "-->", posn_end
        wpts = waypoints(posn_begin, posn_end, npts_per_leg, flightModel, zoneOptions)
        print pandas.DataFrame(wpts)

def run_tests():
    print "\n*** START OF TESTS ***\n"
    test_waypoint_primitives()
    test_cruisePossible()
    test_classifyZone()
    test_waypoints()
    print "\n*** END OF TESTS ***\n"

if __name__ == '__main__':
    run_tests()

