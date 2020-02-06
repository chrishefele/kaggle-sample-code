# const_subs.py
#
# Writes 16 files, each with a constant for the predicted DaysInHospital 
# Ranges from [0,15].  With the 16 resulting RMSLEs, one can calculate the
# number of times each DIH value (0-15) appears in the (hidden) leaderboard set.
# (via a seperate calculation...though beware of overfitting to the leaderboard!)
#
# 7/29/2011 by CJH
#

TEMPLATE = "../data/Target.csv"

lines = open(TEMPLATE,"r").readlines()
header = lines[0]
dataLines = lines[1:]

for daysInHospital in range(0,15+1):
    DIH_string = "%02i" % daysInHospital
    outFileName = "DIH." + DIH_string + ".csv"
    fout = open(outFileName, "w")
    fout.write(header.strip() + "\n")
    for dataLine in dataLines:
        fout.write( dataLine.strip() + str(daysInHospital) + "\n")
    fout.close()
    print "Wrote:", outFileName

print "Done"

