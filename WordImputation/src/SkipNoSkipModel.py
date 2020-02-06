from NGramIndex import NGramIndex
from Cache import Cache
import nltk
import copy
import math
import time 
import cPickle as pickle 
import os.path
import Levenshtein # for edit distance and word median calculations
                   # https://pypi.python.org/pypi/python-Levenshtein/0.11.2
from NGramUtils import positionNGram, positionNGramInverse
from collections import defaultdict
from itertools import izip


MAX_SENTENCES_DEFAULT = 1000


class SkipNoSkipModel:

    """
        To determine the estimated position of the deleted word, the algorithm first 
        creates ngrams from a given sentence. It then then calculates the smoothed 
        probability of seeing each ngram in the ngrams from derived from the corpus,
        vs seeing it in the skip-1-ngrams created from the same corpus.
        (skip-1-ngrams were created from the corpus by creating n+1grams, then 
        deleting a central word). The likely location of the deleted word has the 
        highest ratio between its skip-1-ngram probability and it's ngram probability. 

        Once a position is selected for possible word insertion, the words to 
        the left & right of the insertion point are used with the n+1gram index to 
        determine a list of possible words to insert.  
        A list of possible sentences is returned.

    """

    def __init__(self,  ngrams_file, 
                        skip_ngrams_file, 
                        nplus1grams_file, 
                        cache_file, 
                        unigrams_file,
                        ngram_length, skip_position, min_count ):

        self.ngram_length  = ngram_length
        self.skip_position = skip_position
        
        # The following indexes are used to calculate the ratio of ngram & skip_ngram 
        # prob at each sentence position & find the likely posn of the deleted word
        self.ngrams       = NGramIndex(ngrams_file,      skip_position, False, min_count)
        self.skip_ngrams  = NGramIndex(skip_ngrams_file, skip_position, False, min_count)

        # n+1 grams used to find words that could have been deleted to form the skip_gram
        self.nplus1grams  = NGramIndex(nplus1grams_file, skip_position, True , min_count)

        # a cache is used for compuationally-expensive calculations (e.g. median word)
        self.cache = Cache(cache_file)

    def ngram_at_posn(self, words, word_posn):
        return positionNGram(words, word_posn, self.ngram_length, self.skip_position)

    #def ngram_at_posn_inverse(self, words, word_posn):
    #    return positionNGramInverse(words, word_posn, self.ngram_length, self.skip_position)

    def any_counts(self, ngram):
        return  self.ngrams.get_count(ngram)      > 0  or \
                self.skip_ngrams.get_count(ngram) > 0

    def smoothed_ngram_prob(self, ngram, ngram_index, alpha):
        # Uses a simple additive smoothing algorithm 
        # See http://en.wikipedia.org/wiki/Additive_smoothing
        prob = ( ngram_index.get_count(ngram) + alpha * 1. ) /    \
               ( ngram_index.counts_total     + alpha * ngram_index.num_uniq_ngrams )
        return float(prob) 

    def prob_ratio_at_posn(self, words, word_posn, alpha):
        posn_ngram = self.ngram_at_posn(words, word_posn)
        assert posn_ngram
        ratio = self.smoothed_ngram_prob(posn_ngram, self.skip_ngrams, alpha) / \
                self.smoothed_ngram_prob(posn_ngram, self.ngrams,      alpha) 
        return ratio

    def sentences_given_insert_words(self, sentence_words, insert_words, insert_word_posn):
        sentences = []
        for insert_word in insert_words:
            words = copy.copy(sentence_words)
            # TODO use insert() & pop() instead for speed, instead of copy? 
            words.insert(insert_word_posn + 1, insert_word)
            sentences.append(' '.join(words))
        return sentences

    def sentences_given_insert_posn(self, sent_words, word_posn, 
                                    max_sentences=MAX_SENTENCES_DEFAULT):

        if len(sent_words) < 2:
            sentences = [' '.join(sent_words)]
            counts = [1]
            return sentences, counts

        posn_ngram = self.ngram_at_posn(sent_words, word_posn)
        assert posn_ngram and len(posn_ngram) == self.ngram_length 
        
        # suggestions are a list of tuples ('word',int_count)
        suggestions = list(self.nplus1grams.insert_word_suggestions(posn_ngram))
        suggestions.sort(reverse=True, key=lambda tup: tup[1]) # descending sort by count 
        suggestions = suggestions[:max_sentences] # use top N for fast median string calc 
        insert_words        = [w for w,_ in suggestions]
        insert_words_counts = [c for _,c in suggestions]
        
        # 'ae' is the lowest edit distance word to all unigrams in corpus ::
        # insert_words.append('ae')  # default median word, if no other suggestions  TODO or ''? 
        insert_words.append('')  
        insert_words_counts.append(1) 

        sentences = self.sentences_given_insert_words(sent_words, insert_words, word_posn)
        return sentences, insert_words_counts

