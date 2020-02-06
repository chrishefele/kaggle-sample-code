# parseEssays.py
# by CJH 2/5/2012
#
# usage:  jython parseEssays.py  <input_filename> <essay_sets_to_use>  <output_filename>
#    eg:  jython parseEssays.py  training.tsv   1234   parsed_essays_output.tsv
#         
# Reads the training/input data file and creates a parsed version of the essays.
# Output written to a tab-seperated-field file.
# Only a subset of essay_sets can be identified & parsed; this allows running 
# multiple instances in parallel & merging the resulting files later. 
# 
# example infile:    /home/chefele/Essay/download/release_2/training_set_rel2.tsv

import sys
import os
import string
import time
import EssayParser

# NCOLS_TRAINING = 28 # number of columns/fields in training data

if len(sys.argv) == 4:
    INFILE            = sys.argv[1]
    TARGET_ESSAY_SETS = sys.argv[2]  # e.g.  1 or 23 or 12345678
    OUTFILE           = sys.argv[3]
else:
    print "usage:  jython parseEssays.py  <input_filename> <essay_sets_to_use>  <output_filename>"
    sys.exit()


print "\n***ESSAY PARSER***\n" 
print "Reading from:", INFILE
print "Essay sets  :", TARGET_ESSAY_SETS
print "Writing to  :", OUTFILE
print 

eparser  = EssayParser.EssayParser() # uses Stanford Statistical Parser

print "\nParsing..."
t0 = time.time()
fin  = open(INFILE,  'r')
fout = open(OUTFILE, 'w')

header = fin.readline().split('\t')

for line in fin:
    fields = line.split('\t')
    essay_id, essay_set, essay = fields[0], fields[1], fields[2]

    if essay_set.strip() in TARGET_ESSAY_SETS:
        # remove unprintable characters, which can create errors downstream 
        printable_essay = ''.join(filter(lambda x:x in string.printable, essay))
        parsed_essay, parsed_essay_objs = eparser.parse(printable_essay) # added list of original objects for later use
        outString = '\t'.join([ essay_id, essay_set, parsed_essay ])
        fout.write(outString + '\n')
        print "essay_id:", essay_id, "essay_set:", essay_set, "secs:", int(time.time()-t0)
        sys.stdout.flush()

fin.close()
fout.close()
print "\nDone. Wrote parsed essays to:", OUTFILE,"\n"

