import math
import sys

UNIGRAMS_FILE = '../data/train_ngrams_1+1.txt'
CONCGRAM_FILE = '../data/train_concgrams_3+101.txt'

unigrams_fname = UNIGRAMS_FILE

CONCGRAM_COUNT_TOTAL = 18231255739

if not len(sys.argv)==2:
    print "usage: python concgram_ratios.py <regularization>"
    sys.exit()
PROB_MIN = float(sys.argv[1])


def get_word_probs(unigrams_fname=UNIGRAMS_FILE):
    counts = {}
    tot_counts = 0
    #print "Loading vocabulary from:", unigrams_fname
    for line in open(unigrams_fname, 'rb'):
        tokens = line.rstrip().split()
        assert len(tokens) == 2 
        count = int(tokens[0])
        word  =     tokens[1]   # single word = unigram
        counts[word] = count
        tot_counts += count
    #print len(counts),"vocabulary words loaded from:", unigrams_fname
    #print tot_counts,"words represented"
    #print "min_prob for word: %20.10e" % (1./tot_counts,)
    word_prob = {}
    for word in counts:
        word_prob[word] = float(counts[word]) / tot_counts
    return word_prob

def process_concgram_file(concgram_file):

    word_prob = get_word_probs()

    #print "Processing concgrams from:", concgram_file
    for line in open(concgram_file):
        tokens = line.rstrip().split()
        assert len(tokens) == 3 
        word12_count = int(tokens[0])
        word1, word2 = tokens[1], tokens[2]
        if word2 not in word_prob or word1 not in word_prob: 
            continue

        p_concgram = float(word12_count) / CONCGRAM_COUNT_TOTAL
        p_sentword   = word_prob[word2] 
        p_insertword = word_prob[word1] 
        p_min = PROB_MIN
        ratio = (p_concgram + p_min) / (p_sentword * p_insertword + p_min)
        logratio = math.log10(ratio)
        print "%12.6f %12.6f %10s %10s %20.10e %12.6e %12.6e" % (ratio, logratio, word1, word2, p_concgram, p_sentword, p_insertword)

process_concgram_file(CONCGRAM_FILE)
