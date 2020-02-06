# find_ngrams.py 
# 3/20/2012 by Chris Hefele
#
# usage: python find_ngrams.py <some args> 
#

import sys
import string 
import math 
import numpy
import nltk # natural language toolkit
from nltk.collocations import *

def rmStopWords(text):
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = nltk.wordpunct_tokenize(text)
    nostop = [t.lower() for t in tokens if t.lower() not in stopwords]
    return ' '.join(nostop)

def printableText(text):
    return ''.join(filter(lambda x:x in string.printable, text))

def findNgrams(fin_name):
    print "Finding N-Grams "
    print "Reading from:", fin_name
    fin = open(fin_name,  "r")
    header = fin.readline().split('\t')
   
    eset_texts = {}
    print "Reading essays..."
    for line in fin:
        fields = line.split('\t')
        essay_id, essay_set, essay = fields[0], fields[1], fields[2]
        essay_set = int(essay_set)
        essay = rmStopWords(printableText(essay))
        if essay_set not in eset_texts:
            eset_texts[essay_set] = []
        eset_texts[essay_set].append(essay)
        if int(essay_id) % 100 == 0:
            print essay_id, 
            sys.stdout.flush()
    fin.close()

    print "\nFinding Ngrams..." 
    for eset in eset_texts:
        print "\nEssaySet:", eset
        sys.stdout.flush()
        eset_text = ' '.join(eset_texts[eset])
        tokens = nltk.wordpunct_tokenize(eset_text)
        
        # what to do with these??? 
        bigram_measures  = nltk.collocations.BigramAssocMeasures()
        trigram_measures = nltk.collocations.TrigramAssocMeasures()



        finder = BigramCollocationFinder.from_words(tokens) # change this to read in your data
        finder.apply_freq_filter(3)                         # only bigrams that appear 3+ times
        print "\nFrequent Bigrams"
        for bg in finder.nbest(bigram_measures.pmi, 10):   # return the 10 n-grams with the highest PMI
            print "    ", bg

        """
        scored = finder.score_ngrams(bigram_measures.raw_freq)
        for score,bigram in sorted((score,bigram) for bigram,score in scored):
            print score, bigram

        finder = TrigramCollocationFinder.from_words(tokens) # change this to read in your data
        """

        finder.apply_freq_filter(3)                          # only bigrams that appear 3+ times
        print "\nFrequent Trigrams"
        for bg in finder.nbest(trigram_measures.pmi, 10):   # return the 10 n-grams with the highest PMI
            print "    ",bg

        """
        scored = finder.score_ngrams(trigram_measures.raw_freq)
        for score,trigram in sorted((score,trigram) for trigram,score in scored):
            print score, trigram
        """


    print "\nDone"

# ======   main   =========

FIN  = '/home/chefele/Essay/download/release_3/training_set_rel3.tsv' 
findNgrams(FIN)

