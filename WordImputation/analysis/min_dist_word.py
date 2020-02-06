import itertools
from Levenshtein import distance
import string
import sys

WORD_LEN = int(sys.argv[1])
VOCAB_SIZE = 50000

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
print "Synth word length:", WORD_LEN
print "Vocab words read :", len(vocab_counts)

chars = string.ascii_lowercase + '"\',.?'
min_dist = 999999
for chars in itertools.product(chars, repeat=WORD_LEN):
    word = ''.join(chars)
    tot_dist = 0
    tot_words = 0
    for vocab_word in vocab_counts:
        tot_dist += vocab_counts[vocab_word] * distance(vocab_word, word) 
        tot_words+= vocab_counts[vocab_word]
    avg_dist = float(tot_dist) / tot_words
    if avg_dist < min_dist:
        min_dist = avg_dist
        min_word = word
        print 'new min:', word, avg_dist

