#!/usr/bin/mono /opt/IronPython-2.7.3/ipy64.exe 

print "runProgramModule.py starting"

import clr
import sys
import os

DLL_PATH='/home/chefele/kaggle/FlightQuest2/download/exe'
sys.path.append(DLL_PATH)

# add another DLL
sys.path.append('/home/chefele/kaggle/FlightQuest2/download/src/RunSimulation')

#print sys.path
#print "DLL path files:", os.listdir(DLL_PATH)

clr.AddReferenceToFile('FSharp.Core.dll')
clr.AddReferenceToFile('FlightQuest.dll')
clr.AddReferenceToFile('ProgramModule.dll')

import FlightQuest
print 'dir of FlightQuest:', dir(FlightQuest)
print
from FlightQuest.Spatial import positionToLocation
print 'dir of FlightQuest.Spatial:', dir(FlightQuest.Spatial)
print
print positionToLocation
print positionToLocation(1,2,3)
print

import ProgramModule
from ProgramModule import mainEntry, appSetting
print 'program module dir:', dir(ProgramModule)
print appSetting 
print appSetting("airportsFile")
print appSetting("baseDir")
print mainEntry
print mainEntry(0)


