import ProvidedData
from Transforms import *
from Prediction import *
import scikits.learn.logistic
import math

pd = ProvidedData.ProvidedData()
targetVariable = pd.getTargetVar()
floatDataGetter = makeGetFloatVars(pd.getFloatData)
timestamps = pd.getTimestamps()
selectVar74 = makeSelectVars("Variable74_LASTLASTRETURN")

dataDescription = [ [ normCenter, percentileVars, normCenter, selectVar74, floatDataGetter ] ]
# dataDescription = [ [ normCenter, selectVar74, floatDataGetter ] ]

print "Transforming data"
transformedData = transformData(dataDescription)
# print transformedData

#var74Data = transformedData["Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD"] 
var74Data = transformedData["Variable74_LASTLASTRETURN_CTRMEAN_NORMSTD_PERCENTILE_CTRMEAN_NORMSTD"] 
fracTimestamps = timestamps - numpy.fix(timestamps) 
trainMask = numpy.isfinite(targetVariable) 

fout = open("Var74_Values.csv","w")
for var74Value in var74Data:
    fout.write( str(var74Value)+"\n" ) 
fout.close()
print "Wrote Var74 transformed values to Var74_Values.csv"


