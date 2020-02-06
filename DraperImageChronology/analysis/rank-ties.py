
import itertools
import scipy.stats
import collections

days = (1,2,3,4,5)

#for n, perm in enumerate(itertools.permutations(days, 5)):

"""
results = []

for n, days_pred in enumerate(itertools.product(days, repeat=5)):
    rcor, pval = scipy.stats.spearmanr(days, days_pred)
    if len(set(list(days_pred))) == 2 :
        print n, days_pred, rcor
        results.append( (rcor, n, days_pred) ) 

for result in sorted(results):
    print result

"""

for fill in (1,2,3,4,5):
    for day in (1,2,3,4,5):
        for posn in (1,2,3,4,5):
            pred = 5*[fill]
            pred[posn-1] = day
            rcor, pval = scipy.stats.spearmanr(pred, (1,2,3,4,5))
            print pred, rcor
            #if len(list(set(pred))) == 2:



