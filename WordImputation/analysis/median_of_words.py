import Levenshtein as lev

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

while True:
    print 
    words = raw_input('Enter some predicted  words        : ').strip().split()
    weights= len(words) * [1,]
    median = get_median(words, weights)
    print "\nMedian string of", words, "is", [median]

