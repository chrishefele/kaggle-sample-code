
NLINES = 10000000
TRAIN_FILE = '../download/train_v2.txt'

print "\nUnique words per sentence calculation\n"
print "Reading:", NLINES, "lines from:", TRAIN_FILE

n_words = n_uniq_words = 0
for line_num, line in enumerate(open(TRAIN_FILE,'r')):
    words = line.rstrip().split()
    n_words      += len(    words )
    n_uniq_words += len(set(words))
    if line_num > NLINES:
        break

print n_uniq_words,"words unique to their sentence"
print n_words,     "words in all sentences"
print "Ratio:", float(n_uniq_words)/n_words
print
