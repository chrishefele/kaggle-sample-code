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
    varTrainData = numpy.copy(transformedData[varName][trainMask])
    targetTrainData = numpy.copy(targetVariable[trainMask])
    varCorr = numpy.corrcoef(varTrainData, targetTrainData)[0][1]
    byNameList.append( (varName, varCorr) ) 
    byCorrList.append( (varCorr, varName) ) 

"""
print "\n*** BY NAME ***\n"
for varName, varCorr in sorted(byNameList):
    print varCorr, varName
"""

print "\n*** Corr(Var,TargetVar) ***\n"
for varCorr, varName in sorted(byCorrList):
    print varCorr, varName 


