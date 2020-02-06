import csv
import sys
from itertools import izip

file1 = csv.reader(open(sys.argv[1], 'rb'))
file2 = csv.reader(open(sys.argv[2], 'rb'))

header1, header2 = file1.next(), file2.next()

def parse_words(line):
    sentence_id, sentence = line
    sentence_id = int(sentence_id)
    words = sentence.rstrip().split()
    return words
    
for line1_fields in file1: 
    line2_fields = file2.next()
    words1 = parse_words(line1_fields)
    words2 = parse_words(line2_fields)
    if ' '.join(words1) == ' '.join(words2):
        # print 0 
        continue
    for i, (w1, w2) in enumerate(izip(words1, words2)):
        if w1==w2:
            continue
        else:
            print 1.*i/len(words1)
            # print i
            break



