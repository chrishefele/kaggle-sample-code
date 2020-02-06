import itertools
from Levenshtein import distance
import string
import sys

#VOCAB_SIZE = 50000 # 42 minutes
VOCAB_SIZE = 2000000 # 12 hours? 

vocab_counts = {}
fin = open('../data/1_grams.txt','r')
for line_num, line in enumerate(fin):
    if line_num > VOCAB_SIZE:
        break
    tokens = line.strip().split()
    count = int(tokens[0])
    word  = tokens[1]
    vocab_counts[word] = count
fin.close()
print
print "Vocab words read :", len(vocab_counts)


top10_words = "the , .  to of and a in \" 's".split() # top10 unigrams
other_words = ['','t', 'a','e','ta','at', 'te','et', 'ea'] # baseline '' & combos of 3 most popular letters
median_word = ['ae'] # median word, best 2 char to minimize distance 
words = top10_words + other_words + median_word

for n, word in enumerate(words):
    tot_dist  = 0
    tot_words = 0
    for vocab_word in vocab_counts:
        tot_dist += vocab_counts[vocab_word] * distance(vocab_word, word) 
        tot_words+= vocab_counts[vocab_word]
    avg_dist = float(tot_dist) / tot_words
    print " word: [%4s]  dist: %6.4f" % (word, avg_dist)

# conclusion: picking the most popular WORD does NOT optimize the 
# edit distance vs all the unigrams (i.e the vocabulary).
# Picking the MEDIAN WORD (e.g. 'ae') DOES minimize this. 
# So, don't use the most popular word -- compute the median

