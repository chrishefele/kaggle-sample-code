import sys
sys.path.append("/home/chefele/INFORMS2010/workbench/source")

import ProvidedData
from Transforms import *
import numpy

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
timestamps = pd.getTimestamps()
dataDescription = [[ floatDataGetter ]]
transformedData = transformData(dataDescription)
trainMask = numpy.isfinite(targetVariable) 

byNameList = []
byCorrList = []

var74TrainData = transformedData["Variable74_LASTLASTRETURN"][trainMask]
for varName in transformedData.keys():

    # remove component that var74 will predict 
    varTrainData = numpy.copy(transformedData[varName][trainMask])
    proj = numpy.dot(varTrainData, var74TrainData)/numpy.dot(var74TrainData, var74TrainData)
    varTrainData = varTrainData - proj*var74TrainData

    # remove part of target that is already predicted by var74
    targetTrainData = numpy.copy(targetVariable[trainMask])
    proj = numpy.dot(targetTrainData, var74TrainData)/numpy.dot(var74TrainData, var74TrainData)
    targetTrainData = targetTrainData - proj*var74TrainData

    varCorr = numpy.corrcoef(varTrainData, targetTrainData)[0][1]
    byNameList.append( (varName, varCorr) ) 
    byCorrList.append( (varCorr, varName) ) 

"""
print "\n*** BY NAME ***\n"
for varName, varCorr in sorted(byNameList):
    print varCorr, varName
"""

print "\n*** Corr( (Var-Var74), (TargetVar-Var74) ) ***\n"
for varCorr, varName in sorted(byCorrList):
    print varCorr, varName 


