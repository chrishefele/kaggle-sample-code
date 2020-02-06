import random
import time
import gc
import sys
from itertools import izip
from SkipNoSkipModel import SkipNoSkipModel
from BackoffModel import BackoffModel
from Levenshtein import distance as edit_distance
from sorted_model_masks import sorted_model_masks

HOLDOUT_FILE = '../data/holdout.txt'
RAND_SEED    = 42


def print_err_type(sent_orig, sent_predict, sent_default):

    err = edit_distance(sent_orig, sent_predict)
    words_orig    = sent_orig.split(' ')
    words_predict = sent_predict.split(' ')
    words_default = sent_default.split(' ')

    if sent_predict == sent_default:
        err_type = "no_position"
    else:

        if len(words_predict) != len(words_orig):
            print "EXCEPTION: sentence length mismatch:"
            print "words_predict:", len(words_predict), words_predict
            print "words_orig   :", len(words_orig),    words_orig
            return

        n_words_diff = sum( w1!=w2 for w1, w2 in izip(words_predict, words_orig))
        posn_right = (n_words_diff <= 1)
        if posn_right:
            err_type = "right_position" 
        else: 
            err_type = "wrong_position"

    added_chars = len(sent_predict) - len(sent_default)
    print "ERROR err:", err, "err_type:", err_type, "added_chars:", added_chars


def calc_improvement(model, reg, max_lines=None):

    random.seed(RAND_SEED)
    err_default = 0
    err_predict = 0

    holdout = open(HOLDOUT_FILE, 'r')
    for line_num, line in enumerate(holdout):
        words = line.rstrip().split()
        if max_lines and line_num > max_lines:
            break
        if len(words) > 2: 
            del_word_posn = random.randint(1, len(words)-2)
            del_word = words[del_word_posn]
            words_orig = words
            words = words[0:del_word_posn] + words[(del_word_posn+1):]
        else:
            words_orig = words

        sent_orig    =  ' '.join(words_orig)
        sent_default =  ' '.join(words)
        sent_predict = model.best_sentence(words, reg)

        err_orig_default = edit_distance(sent_orig, sent_default)
        err_default += err_orig_default
        err_orig_predict = edit_distance(sent_orig, sent_predict)
        err_predict += err_orig_predict

        if False: # DEBUG print  
            print 
            print "sentence#:", line_num
            # print_err_type(sent_orig, sent_predict, sent_default)
            print "deleted_word:", del_word, 
            print "pred_err:", edit_distance(sent_orig, sent_predict)
            for tag, s in [('orig:', sent_orig), ('dflt:', sent_default), ('pred:', sent_predict)]:
                print tag, edit_distance(sent_orig, s), s 

        improvement = float(err_default - err_predict)/err_default
        #print "cumulative improvement:", improvement

    holdout.close()
    improvement = float(err_default - err_predict)/err_default
    return improvement

# -----------------------------------------------------------------------

def main():

    #MIN_COUNT     = 3000          # don't include n-grams with <MIN_COUNT occurences  
    MIN_COUNT      = 3             # don't include n-grams with <MIN_COUNT occurences  

    # HOLDOUT_SIZE  = 300*1000     
    HOLDOUT_SIZE   = 10*1000     # NOTE make 10K for fast testing

    # regs used to regularize the ngram probability calculations
    # regs = [0.01, 0.1, 1, 10, 100]
    regs = [1,]


    print "\n*** Scoring holdout set ***\n"
    print "holdout size  :", HOLDOUT_SIZE
    print "regs          :", regs
    print "min_count     :", MIN_COUNT

    best_model_mask     = ('1101','1011', '101' )
    #baseline_model_mask = (               '101',)

    #for model_masks in sorted_model_masks(): # 80 candidate model masks
    #for model_masks in (baseline_model_mask,):
    for model_masks in (best_model_mask,):

        print "\n*** Initializing new set of backoff models using masks:", model_masks, " ***\n"
        model = BackoffModel(masks=model_masks, min_count=MIN_COUNT)

        print 'Starting to score the holdout set' 
        for reg in regs:
            t0 = time.time()
            improvement = calc_improvement(model, reg, max_lines=HOLDOUT_SIZE)
            secs = time.time() - t0
            values = (MIN_COUNT, reg, improvement, secs)
            print "RESULT min_count: %3i reg: %8.2f improve: %8.4f secs: %8.2f" % values , 
            print model_masks

        model.save_cache()

        del model # large multi-GB object
        gc.collect()


main()

