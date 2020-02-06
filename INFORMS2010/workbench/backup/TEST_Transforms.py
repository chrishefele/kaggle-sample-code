import ProvidedData
from Transforms import *

pd = ProvidedData.ProvidedData()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
dataDescription = [ [normStd, centerMean, floatDataGetter], \
                    [normStd, centerMean, doPCA, normStd, centerMean, floatDataGetter], \
                    [gradientVars, integrateVars, normStd, centerMean, floatDataGetter],\
                    [diffVars , integrateVars, normStd, centerMean, floatDataGetter]  ]  

print "Transforming data"
transformedData = transformData(dataDescription)
print transformedData

