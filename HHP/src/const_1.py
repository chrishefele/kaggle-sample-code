# const_1.py
#
# Writes a constant 1 prediction for DaysInHospital
# RMSLE of this is useful for leaderboard-feedback based blending


OUTFILE  = '../consts/const_1.csv'
TEMPLATE = '../download/HHP_release3/Target.csv'

# Target.csv template file format is as follows:
# MemberID,ClaimsTruncated,DaysInHospital
# 20820036,0,
# 14625274,1,

fin = open(TEMPLATE,'r')
header = fin.readline()

fout=open(OUTFILE, 'w')
fout.write('MemberID,DaysInHospital\n')

for line in fin:
    member_id = line.split(',')[0]
    fout.write( member_id + ', 1\n')

print "Wrote:", OUTFILE
