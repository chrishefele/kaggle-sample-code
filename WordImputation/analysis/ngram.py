import nltk

NGRAM = 4

fin = open('../download/train.txt','r')
for n, line in enumerate(fin):
    words = line.rstrip().split()
    ngrams = nltk.util.ngrams(words, NGRAM)
    for ngram in ngrams:
        print ' '.join(ngram)
fin.close()

