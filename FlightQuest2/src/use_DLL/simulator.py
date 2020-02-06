#!/usr/bin/mono /opt/IronPython-2.7.3/ipy64.exe 

import clr
import sys

DLL_PATH='/home/chefele/kaggle/FlightQuest2/FlightQuestSimulator-Rev2/exe'

sys.path.append(DLL_PATH)

print sys.path

clr.AddReferenceToFile('FSharp.Core.dll', 'FlightQuest.dll')

import FlightQuest
from FlightQuest.Spatial import positionToLocation, positionToAltitude

#for n, rf in enumerate(clr.References): 
#    print n, rf

# above shows FSharp.Core already loaded
# import FSharp.Core
# print dir(FSharp.Core)

# from F# code
# let positionToLocation (x,y,_) = (x,y)
# let positionToAltitude (_,_,z) = z

#print positionToLocation
#print positionToLocation(1,2,3)
#print positionToAltitude(1,2,3)

print "Hello from the simulator-driver code!"

import FlightQuest.Aircraft
print dir(FlightQuest.Aircraft)
print dir(FlightQuest.Aircraft.AircraftType)
print FlightQuest.Aircraft.mediumRange.FuelCapacity
aircraft = FlightQuest.Aircraft.AircraftType(1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7)
print aircraft.FuelCapacity

#import    Microsoft.FSharp.Collections 
#print dir(Microsoft.FSharp.Collections)

# from http://www.gequest.com/c/flight2/forums/t/5570/how-to-play-with-the-toy/29703#post29703
# To read SimulatorResults.Messages, you simply need to reference 
# FSharp.Core (v.4) via NuGet to get FSharpList. 
# The only lengthy task at hand is loading the data files. 
# Obviously, you'll want to use the same Serialization.loadXYZFromFile functions as seen in Program.fs.
# Take a look at the functions/items available under FlightQuest.Simulator for simulating single flights.
