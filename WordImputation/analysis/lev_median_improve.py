import Levenshtein as lev
import sys

MAX_LINES = 100000

def get_median(words, counts):
    median = lev.median(words, counts)
    print median,
    while True:
        last_median = median
        median = lev.median_improve(median, words, counts)
        print "-->", median,
        if median == last_median:
            break
    return median 

for MAX_LINES in [pow(2,n) for n in range(17+1)]:
    counts = []
    words  = []
    #fin = open('../data/1_grams.txt','r')
    fin = open('../data/old/1_grams.txt','r')
    for line_num, line in enumerate(fin):
        if line_num > MAX_LINES:
            break
        tokens = line.rstrip().split()
        count = int(tokens[0])
        word  = tokens[1]
        counts.append(count)
        words.append(word)
    fin.close()
    # print "iterating median word calculation: ",
    print MAX_LINES, 
    get_median(words, counts)
    print


