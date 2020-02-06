import Levenshtein as lev
import sys

def get_median(words, counts):
    median = lev.median(words, counts)
    # print median,
    while True:
        last_median = median
        median = lev.median_improve(median, words, counts)
        # print "-->", median,
        if median == last_median:
            break
    return median 


for wt in xrange(2*100):
    #wordlist = ['beginning', 'ending']
    wordlist = ['abcdefghij', 'efghijklmnopq']
    weights  = [ 100, wt ]
    print wt, get_median(wordlist, weights)
    





