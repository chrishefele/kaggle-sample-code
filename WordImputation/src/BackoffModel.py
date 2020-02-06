from SkipNoSkipModel import SkipNoSkipModel
from Cache import Cache
import copy
import numpy as np
import Levenshtein
import collections
import time

DATA_DIR        = '../data/'
CACHE_FILE      = '../data/cache_BackoffModel.pkl'
MAX_WEIGHT_INT  = 1000

MEDIAN_CALC_TOP_N = 40 
#MEDIAN_CALC_TOP_N = 20 # maximum number of sentences to send to the median sentence 
                       # calculation, which is computationally intensive

class BackoffModel:

    def __init__(self, masks=('11011','101'), min_count=5):

        self.init_models(masks, min_count)
        self.cache = Cache(CACHE_FILE)

    def init_models(self, desired_ngram_masks, min_count):
        # NOTE desired_ngram_masks selects model backoff 
        # sequence, from longest ngrams to shortest ngram.
        print "Backoff sequence (ngram model masks):", desired_ngram_masks

        self.models = []
        models_params = [('11101', 4, 2), 
                         ('11011', 4, 1), 
                         ('10111', 4, 0), 
                         ('1101',  3, 1), 
                         ('1011',  3, 0), 
                         ('101',   2, 0)] 

        for ngram_mask, ngram_length, skip_posn in models_params:
            if ngram_mask in desired_ngram_masks:
                n                   = ngram_length
                datdir              = DATA_DIR
                ngrams_file         = datdir + 'train_ngrams_' + str(n)   + \
                                               '+' + (n  )*'1'  + '.txt'
                skip_ngrams_file    = datdir + 'train_ngrams_' + str(n+1) + \
                                                '+' + ngram_mask + '.txt'
                nplus1grams_file    = datdir + 'train_ngrams_' + str(n+1) + \
                                                '+' + (n+1)*'1'  + '.txt'
                cache_file          = datdir + 'cache_'        + str(n+1) + \
                                                '+' + ngram_mask + '.pkl'
                unigrams_file       = datdir + 'train_ngrams_1+1.txt'

                model = SkipNoSkipModel( ngrams_file, skip_ngrams_file, nplus1grams_file, 
                                         cache_file, unigrams_file,
                                         ngram_length, skip_posn, min_count)
                self.models.append(model)
      
    def save_cache(self):
        self.cache.save_cache()

    def median_string(self, strings, string_counts):
        # Find a 'median string' which is a string with the minimal
        # sum of edit distances to each string in a list of strings. 
        # see: https://pypi.python.org/pypi/python-Levenshtein/0.11.2
        # Note the python package above also permits the use of 
        # weights for each string (e.g. counts of occurances)
        median = Levenshtein.median(strings, string_counts)
        while True:
            last_median = median
            median = Levenshtein.median_improve(median, strings, string_counts)
            if median == last_median:
                break
        return median
        
    def median_sentence_calc(self, sentences, sentence_counts):
        return  self.median_string(sentences, sentence_counts)

    def median_sentence_cache(self, sentences, sentence_counts):
        key = tuple(zip(sentences, sentence_counts))
        h = hash(key)
        if h not in self.cache:
            self.cache[h] = self.median_sentence_calc(sentences, sentence_counts)
            self.cache.print_cache_stats()
        return self.cache[h]


    def sentences_and_weights(self, words, alpha): 

        if len(words) > 100: # avoid median calc on rare very long sentences
            return [' '.join(words)], [1]

        sentence_weights = collections.defaultdict(float)
        max_sent_weight = 0.0

        for posn in xrange(len(words)-1):
            # backoff through progressively smaller N-gram models, 
            # until we find a valid N-gram that's been seen before.
            for model in self.models:
                ngram = model.ngram_at_posn(words, posn) 
                if ngram and model.any_counts(ngram): 
                    break
            else:
                # for unknown ngrams, default to smallest ngram model 
                model = self.models[-1] 

            ratio             = model.prob_ratio_at_posn(words, posn, alpha) 
            sentences, counts = model.sentences_given_insert_posn(words, posn)
            counts            = np.array(counts, dtype=float)
            weights           = ratio * counts / counts.sum()

            for sentence, weight in zip(sentences, weights):
                sentence_weights[sentence] += weight
                max_sent_weight = max(max_sent_weight, sentence_weights[sentence])
        
        wt_sent_tups = []
        for sentence in sentence_weights:
            weight = int(MAX_WEIGHT_INT * sentence_weights[sentence] / max_sent_weight)
            if weight > 0:
                wt_sent_tups.append((weight, sentence))
        wt_sent_tups.sort(reverse=True)
        top_n = MEDIAN_CALC_TOP_N
        sentences   = [sent for wt, sent in wt_sent_tups][:top_n]
        int_weights = [wt   for wt, sent in wt_sent_tups][:top_n]
        return sentences, int_weights

    def print_sentences_weights(self, sentences, weights):
        assert len(sentences) == len(weights)
        print
        for w, s in zip(weights, sentences):
            print [w], s
        print "TotalSentences:", len(sentences) 

    def median_sentence(self, words, alpha, insert_word=None):
        sentences, weights = self.sentences_and_weights(words, alpha)

        self.print_sentences_weights(sentences, weights)

        print "Calculating median of %s sentences above" % len(sentences)
        t0 = time.time()
        median_sentence_ = self.median_sentence_cache(sentences, weights)
        print "MEDIAN:\n", median_sentence_
        print "TIME:", time.time() - t0, "N_sentences:", len(sentences),
        print "N_Sent_Chars:", len(' '.join(words))
        print 

        return median_sentence_
    
    def best_sentence(self, words, alpha, insert_word=None):
        # words         : list of sentence words
        # alpha         : a regularization factor for ngram prob smoothing (generally, use 1).
        # insert_word   : if a string given, overrides the best_insert_word calcluation 
        if len(words) < 2:
            return ' '.join(words)
        else:
            return self.median_sentence(words, alpha, insert_word=insert_word)

