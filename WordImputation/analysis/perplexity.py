import sys
import math

ngram_fname = sys.argv[1]

def parse_count_ngram(line):
    tokens = line.rstrip().split()
    count = int(tokens[0])
    ngram = ' '.join(tokens[1:]) + ' ' 
    return (count, ngram)

sum_counts = sum_lengths = uniq_ngrams = 0

ngram_file = open(ngram_fname, 'r')
for line in ngram_file:
    count, ngram = parse_count_ngram(line)
    sum_counts  += count
    sum_lengths += count * len(ngram) 
    uniq_ngrams += 1
ngram_file.close()

print "ngrams in corpus:", sum_counts
print "unique ngrams   :", uniq_ngrams
mean_ngram_length = float(sum_lengths)/sum_counts
print "mean ngram length:", mean_ngram_length

entropy = 0
log2 = math.log(2)
for line in open(ngram_fname,'r'):
    count, ngram = parse_count_ngram(line)
    p = float(count) / sum_counts
    entropy += -p * math.log(p) / log2

print "tot entropy (bits/ngram):", entropy
print "entropy per char  (bits):", entropy / mean_ngram_length

