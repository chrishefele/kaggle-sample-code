# cleanEssays.py
# usage:  python cleanEssays.py  input_filename   output_filename
# Rewrites the input training file, stripping out unprintable characters in the essay 
# by CJH 2/6/2012

import sys, string

INFILE  = sys.argv[1]  
OUTFILE = sys.argv[2]
fin  = open(INFILE,  'r')
fout = open(OUTFILE, 'w')

header = fin.readline()
fout.write(header)

for line in fin:
    fields = line.split('\t')
    essay = fields[2] 
    # filter out unprintable characters, which can create errors downstream 
    printable_essay = ''.join( filter(lambda x:x in string.printable, essay) )
    fields[2] = printable_essay
    outString = '\t'.join(fields)
    fout.write(outString)
    
fin.close()
fout.close()

