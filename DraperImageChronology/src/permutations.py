
import itertools
import scipy.stats


truth = (1,2,3,4,5)

for n, perm in enumerate(itertools.permutations((1,2,3,4,5), 5)):
    
    rcor, pval = scipy.stats.spearmanr(truth, perm)
    print n, perm, rcor

