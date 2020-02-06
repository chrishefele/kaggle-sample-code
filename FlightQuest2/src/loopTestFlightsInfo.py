from gcUtils import gcIntermediate, gcDistMile
from testFlightsInfo import testFlightsInfo

for f in testFlightsInfo():
    fid     =  f['FlightHistoryId']
    pt1     = (f['CurrentLatitude'], f['CurrentLongitude'])
    pt2     = (f['ArrivalLatitude'], f['ArrivalLongitude'])
    alt1    =  f['CurrentAltitude']
    alt2    =  f['ArrivalAltitude']
    gspd1   =  f['CurrentGroundSpeed']
    gspd2   =  0 # 0, or try a realistic landing velocity? 

    #print fid,': ',pt1,alt1,gspd1,'-->',pt2,alt2,gspd2,'gcDistMile:',gcDistMile(pt1,pt2)
    print fid,': ','alt/spd:',alt1,gspd1,'-->',alt2,gspd2,'gcDistMile:',gcDistMile(pt1,pt2)

    # print waypoints(fid, pt1, pt2, alt1, alt2)

# a sample of available flight info fields is below
"""
FlightHistoryId                           301897853
CutoffTime                2013-07-05 21:56:51+00:00
ArrivalAirport                                 KSEA
ScheduledArrivalTime      2013-07-05 23:30:00+00:00
CurrentLatitude                               41.23
CurrentLongitude                            -112.63
CurrentAltitude                               40000
CurrentGroundSpeed                              436
StandardPassengerCount                          105
PremiumPassengerCount                            13
FuelRemainingPounds                        16428.16
FuelCost                                        1.9
CrewDelayCost                                614.09
OtherHourlyCosts                            1783.96
NonarrivalPenalty                            100000
DelayCostProportion30m                        0.293
DelayCostProportion2h                         0.357
MaxStandardDelayCost                          35.91
MaxPremiumDelayCost                           90.65
ArrivalLatitude                               47.45
ArrivalLongitude                           -122.312
ArrivalAltitude                                 433
"""
