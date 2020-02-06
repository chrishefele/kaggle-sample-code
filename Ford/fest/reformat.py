# program to reformat csv data files to svmlight/libsvm data files
# usage: python reformat.py  infile.csv  outfile.svmlight

import sys

fin_name  = sys.argv[1]
fout_name = sys.argv[2]

print "reading csv data file from    :",fin_name
print "writing svmlight data file to :",fout_name

fin =  open(fin_name, "r")
fout = open(fout_name,"w")

header = fin.readline()
for line in fin:
    tokens = line.split(",")
    features = [f.strip() for f in tokens[3:]]  # TrialID, ObsNum, IsAlert, features...
    out_features = [ str(fnum+1)+":"+fval.strip()+" " for fnum,fval in enumerate(features) ]
    target = tokens[2].strip()
    if target == "?":
        target = 0
    elif target == "1":
        target = "+1"
    elif target == "0":
        target = "-1"
    else:
        raise(ValueError)
    outstring = str(target) + " " + (''.join(out_features))
    fout.write(outstring + "\n")

fout.close()

