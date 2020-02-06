# spaces.py -- tabulates the lengths contiguous spaces in each essay
#              The intent is to try to detect paragraph breaks 

TRAINING_FILE   = "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
OUTPUT_FILE     = 'spaces.csv'
SPACE           = ' '

def essaySpaceCounts(essay):
    s = [c for c in essay]
    space_counts = []
    while s:
        space_count = 0
        while s and s[0]==SPACE:
            s.pop(0)
            space_count += 1
        if space_count:
            space_counts.append(space_count)
        while s and s[0]!=SPACE:
            s.pop(0)
    return space_counts


# --- main ---

print "Finding the lengths of contiguous spaces in each essay"
fin  = open(TRAINING_FILE,'r')
fout = open(OUTPUT_FILE,  'w')
fout.write('essay_id,essay_set,count\n')
for line in fin:
    fields = line.split('\t')
    essay_id, essay_set, essay = fields[0], fields[1], fields[2]
    for count in essaySpaceCounts(essay):
        outstring = essay_id + ',' + essay_set + ',' + str(count)
        fout.write(outstring+"\n")

print "Wrote results to:", OUTPUT_FILE


""" TEST CODE
print essaySpaceCounts('')
print essaySpaceCounts('    ')
print essaySpaceCounts('abcd')
print essaySpaceCounts('     abcd')
print essaySpaceCounts('abcd     ')
print essaySpaceCounts('    abcd     ')
print essaySpaceCounts('abcd     efgh')
print essaySpaceCounts('abcd     efgh    ')
print essaySpaceCounts('    abcd     efgh')
"""



