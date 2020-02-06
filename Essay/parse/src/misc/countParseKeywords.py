# countParseKeywords.py
# by CJH 2/6/2012

import sys, string

INFILE  = sys.argv[1]  
fin  = open(INFILE,  'r')

counts = {}
for line in fin:
    fields = line.split('\t')
    essay = fields[2] 
    # filter out unprintable characters, which can create errors downstream 
    printable_essay = ''.join( filter(lambda x:x in string.printable, essay) )
    parseKeywords = [ token for token in printable_essay.split() if token[0]=='(' ]  
    for parseKeyword in parseKeywords:
        if parseKeyword not in counts:
            counts[parseKeyword] = 0
        counts[parseKeyword] += 1

fin.close()

for cnt, kwd in sorted([ (counts[kw], kw) for kw in counts ]):
    print kwd, cnt
    
