# split.py
# 1/26/2012 by Chris Hefele
#
# This program takes a train/test/validation format file & splits them into
# multiple files, one per essay. This is the format needed by the R LSA routines.

DATA_DIR = "/home/chefele/Essay/download/release_2/"
DATA     = "training_set_rel2.tsv"

DIR_OUT  = "split.out"

import sys
import os, os.path
import string

print "Splitting essays into individual files" 
print "Reading from:", DATA_DIR+DATA

fin = open(DATA_DIR+DATA, "r")
if not os.path.exists(DIR_OUT):
    os.mkdir(DIR_OUT)

header = fin.readline().split('\t')
for line in fin:

    fields = line.split('\t')
    essay_id, essay_set, essay, domain1_score = fields[0], fields[1], fields[2], fields[6]
    # remove unprintable characters, which create R LSA routine errors (in 'textmatrix')
    printable_essay = ''.join(filter(lambda x:x in string.printable, essay))

    fout = open(DIR_OUT+"/"+essay_id.strip(), 'w')
    fout.write(printable_essay+"\n")
    fout.close()

    if int(essay_id) % 100 == 0:
        print essay_id, 
        sys.stdout.flush()

fin.close()
print "\nDone. Wrote to directory:", DIR_OUT

