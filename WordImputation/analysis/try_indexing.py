# note:  90% memory use after about 40M lines indexed (out of 189M for 3-grams)

import sys
from collections import defaultdict

fin = open("n3gram.txt")

tree = lambda: defaultdict(tree)
index = tree()

for n, line in enumerate(fin):
    tokens = line.rstrip().split()
    count = int(tokens[0])
    word1, word2, word3 = tokens[1], tokens[2], tokens[3]
    index[word1][word2][word3] = count
    if n % 100000 == 0:
        print "\r", float(n)/1000000,"million",
        sys.stdout.flush()


