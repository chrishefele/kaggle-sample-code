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
    target      = raw_input('Enter a target (ground-truth) word : ').strip()
    predictions = raw_input('Enter some predicted  words        : ').strip().split()
    print

    # get distance for each predicted word, as well as their average
    dist_tot = 0     
    for word in predictions: 
        dist = lev.distance(target, word)
        print "%4i = edit_distance(%s, %s)" %  (dist, target, word)
        dist_tot += dist
    dist_avg_pred = 1.*dist_tot/len(predictions)
    print
    print "Average edit_distance between each predicted word and the target word",
    print [target], "is:", dist_avg_pred

    # get the distance for the median word  (to compare)
    weights= len(predictions) * [1,]
    median = get_median(predictions, weights)
    print "\nMedian string of", predictions, "is", [median]
    dist_median    = 1.*lev.distance(target, median)
    print "Edit_distance from the median string", [median],
    print " to the target word ", [target], "is:", dist_median
    print "\n-----"



