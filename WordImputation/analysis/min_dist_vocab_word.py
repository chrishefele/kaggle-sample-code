import itertools
from Levenshtein import distance
import string
import sys

#VOCAB_SIZE = 50000 # 42 minutes
VOCAB_SIZE = 200000 # 12 hours? 

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

min_dist = 999999
for n, word in enumerate(sorted(vocab_counts)):
    tot_dist  = 0
    tot_words = 0
    for vocab_word in vocab_counts:
        tot_dist += vocab_counts[vocab_word] * distance(vocab_word, word) 
        tot_words+= vocab_counts[vocab_word]
    avg_dist = float(tot_dist) / tot_words
    if avg_dist < min_dist:
        min_dist = avg_dist
        min_word = word
        print '\nNew minimum :', word, avg_dist
    if n % 100 == 0:
        print n,
        sys.stdout.flush()

