

DATA_DIR = "/home/chefele/Essay/download/release_2/"
DATA     = "training_set_rel2.tsv"

import sys
import os, os.path
import string

print "Splitting essays into individual files" 
print "Reading from:", DATA_DIR+DATA

fin = open(DATA_DIR+DATA, "r")

essay_set_counts = {}

header = fin.readline().split('\t')
for line in fin:

    fields = line.split('\t')
    essay_id, essay_set, essay, domain1_score = fields[0], fields[1], fields[2], fields[6]
    # remove unprintable characters, which create R LSA routine errors (in 'textmatrix')
    printable_essay = ''.join(filter(lambda x:x in string.printable, essay))

    if essay_set not in essay_set_counts:
        essay_set_counts[essay_set] = 1
    else:
        essay_set_counts[essay_set] += 1

    if int(essay_id) % 100 == 0:
        print essay_id, 
        sys.stdout.flush()

fin.close()
print "\nDone."
print essay_set_counts

