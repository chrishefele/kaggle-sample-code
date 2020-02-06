# unclean.py
# Finds essays with unprintable characters in the essay 
# by CJH 2/8/2012

import sys, string

INFILE  = sys.argv[1]  
fin  = open(INFILE,  'r')

header = fin.readline()

notprintable = 0 
char_counts = {}
for line in fin:
    printable = True
    fields = line.split('\t')
    essay_id, essay_set, essay = fields[0], fields[1], fields[2] 
    for c in essay:
        if c not in char_counts:
            char_counts[c] = 0
        char_counts[c] += 1
        if ord(c)>=127:
            printable = False
    if not printable:
        print essay_id
        notprintable += 1
fin.close()

sq = "\'"
for c in sorted(char_counts):
    print "char:", sq+c+sq, "char_code:", ord(c), "count:", char_counts[c]

print "Num notprintable:", notprintable

print "char_code\tcount"
for c in sorted(char_counts):
    if ord(c) >=127:
        print ord(c),"\t\t",char_counts[c]



