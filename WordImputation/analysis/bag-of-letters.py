# program to assess what fraction of words can be identified using
# only their letter counts (bag-of-letters), and NOT the ordering of
# those letters (e.g. a Scrabble-tile-like problem)
#
# Motivation: Could we use just the letter counts to represent a word?
# This would keep the feature dimentionality down 
# Maybe just use H hash functions to map the word to bits in N dimensions?
# where H << N, e.g. 10 bits in 100 dimensions.

from collections import defaultdict
import re

UNIGRAMS_FILE = "../data/train_ngrams_1+1.txt"
MIN_COUNT = 2
MAX_RANK = 50*1000

_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

same_letters = defaultdict(list)

for rank, line in enumerate(open(UNIGRAMS_FILE,'r'), start=1):
    count, word = line.rstrip().split()
    count = int(count)

    if count < MIN_COUNT:
        break
    if contains_digits(word):
        continue
    if rank > MAX_RANK:
        break 

    key = ''.join(sorted(list(word)))
    same_letters[key].append((count, word))

collision_wordcount = 0
uniq_wordcount  = 0 

sorted_by_collisions = sorted([(len(same_letters[key]), key) for key in same_letters])
for collisions, key in sorted_by_collisions:
    wordcount = sum([cnt for cnt,wrd in same_letters[key]])
    if collisions > 1:
        collision_wordcount += wordcount
        print "Anagrams for letters:", key, "->", same_letters[key]
    else:
        uniq_wordcount += wordcount

print
print "INPUT VOCABULARY STATS"
print "vocabulary file    :", UNIGRAMS_FILE 
print "min word count     :", MIN_COUNT 
print "max word rank      :", MAX_RANK 
print
print "RESULTS"
print "uniq wordcount     :", uniq_wordcount
print "collision wordcount:", collision_wordcount 
print "uniq fraction      :", float(uniq_wordcount) / (collision_wordcount+uniq_wordcount)
print
print "(uniq fraction is the fraction of all vocab  words that can be uniquely identifed"
print "by ONLY their letter counts, regardless of their order)"
print



