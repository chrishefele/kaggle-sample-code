import numpy
import pickle
import sys
if len(sys.argv)!=3:
    print "syntax:   PredFileToText <infile> <outfile>"
    exit()

def loadPredictionsFile(inFileName): 
    print "Reading predictions from:", inFileName 
    fin = open(inFileName, "r")
    predDict = pickle.load(fin)
    fin.close()
    return predDict

predDict = loadPredictionsFile(sys.argv[1])
key = predDict.keys()[0]
predictions = predDict[key]
trainingMask = numpy.isfinite(predictions)

fout = open(sys.argv[2],"w")
for prediction in predictions[trainingMask]:
    fout.write(str(prediction)+"\n")
fout.close()
print "Wrote text training predictions to:",sys.argv[2]

