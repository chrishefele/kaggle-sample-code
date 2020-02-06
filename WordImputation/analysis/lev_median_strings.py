import Levenshtein as lev

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

print "\nCalculating string median"
strings = [  'one alpha bravo charlie', 
             'alpha one bravo charlie', 
             'alpha bravo one charlie', 
             'alpha bravo charlie one']
weights = [888,1000,1321,1111]

median = get_median(strings, weights)

print "\nMEDIAN of:", strings, "with weights:", weights, "is:", median

