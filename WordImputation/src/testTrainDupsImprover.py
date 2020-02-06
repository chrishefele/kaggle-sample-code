# usage: python testTrainDupsImprover.py <submission_infile> <improved_submission_outfile>
# 
# This code takes advantage of the observation that there are about 1%
# of lines are duplicates, and some of those are in BOTH the test & train sets. 
# One can improve submissions by finding very closely matching lines by
# comparing a submission's lines with lines in the training set.
# If there is a very close match, the training set line
# is substituted for the line in the original submission. 
#

import csv
import sys
from collections import defaultdict
from Levenshtein import distance as edit_distance
import cPickle as pickle
import os.path

TEST_FILE           = '../download/test_v2.txt'
TRAIN_FILE          = '../download/train_v2.txt'
SUBSTITUTIONS_FILE  = '../data/cache.testTrainDupsImprover.pkl'
PRINT_STATUS_MOD    = 100000 # print status interval during long caculations 

def test_sentence_reader():
    test_file  = csv.reader(open(TEST_FILE, 'rb'))
    header = test_file.next()
    for line in test_file:
        sentence_id, sentence = line
        sentence_id = int(sentence_id)
        yield sentence_id, sentence

def train_sentence_reader():
    train_file = open(TRAIN_FILE, 'rb')
    for line_num, line in enumerate(train_file, start=1):
        print_status(line_num)
        yield line.rstrip()

def print_status(line_num):
    if line_num % PRINT_STATUS_MOD == 0:
        print "%iK" % (line_num/1000,)  , 

def del_sentences(sentence):
    # return a series of sentences, each has an interior words deleted 
    words = sentence.split()
    for del_posn in range(1, len(words)-1):
        del_word    = words[del_posn]
        left_words  = words[            :del_posn] 
        right_words = words[(del_posn+1):        ]
        del_sentence = ' '.join(left_words + right_words)
        yield del_sentence


def get_substitutions(fname=SUBSTITUTIONS_FILE):
    if os.path.isfile(fname):
        print "Loading substitutions from:", fname
        substitutions = pickle.load(open(fname, 'rb'))
    else:
        print "Calculating substitutions"
        substitutions = calc_substitutions()
        print "Saving substitutions to:", fname
        pickle.dump(substitutions, open(fname, "wb"))
    return substitutions


def calc_substitutions():
    # find very similar lines that are in both test & training sets
    sent_to_id      = {}
    id_to_sent_subs = {}
    for sent_id, sent in test_sentence_reader():
        sent_to_id[sent] = sent_id
        id_to_sent_subs[sent_id] = []

    # Find and save training set sentences with 1 word deleted 
    # that also happen to be in the test set.
    for sentence in train_sentence_reader():
        for del_sentence in del_sentences(sentence):
            if del_sentence in sent_to_id: 
                id_ = sent_to_id[del_sentence]
                id_to_sent_subs[id_].append(sentence)

    # Return only sentences that have a unique match between test & train
    substitutions = {}
    for id_ in id_to_sent_subs:
        if len(id_to_sent_subs[id_]) == 1: # unique match
            substitutions[id_] = id_to_sent_subs[id_][0]

    return substitutions # substitutions[sent_id] -> sentence 
        

def write_improved_submission(infile_name, outfile_name, substitutions):
    infile  = csv.reader(open(infile_name,  'rb'))
    outfile = csv.writer(open(outfile_name, 'wb'), quoting=csv.QUOTE_NONNUMERIC)
    header = infile.next()
    outfile.writerow( header )

    nlines = 0 
    errs_fixed = 0 
    for line in infile:
        sentence_id, sentence = line
        sentence_id = int(sentence_id)
        if sentence_id in substitutions:
            new_sentence = substitutions[sentence_id]
            errs_fixed += edit_distance(new_sentence, sentence)
        else:
            new_sentence = sentence
        nlines += 1
        outfile.writerow( (sentence_id, new_sentence) ) 

    err_improvement = float(errs_fixed) / nlines
    print "Estimated improvement:", err_improvement


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "usage: python testTrainDupsImprover.py",
        print "<submission_infile> <improved_submission_outfile>"
        sys.exit()

    infile_name, outfile_name = sys.argv[1], sys.argv[2]

    print '\n*** Word Imputation Contest - Submission Improver ***\n' 
    print 'Original submission will be read from  :', infile_name
    print 'Improved submission will be written to :', outfile_name

    substitutions = get_substitutions() 
    print "Number of substitutions found :", len(substitutions)

    write_improved_submission(infile_name, outfile_name, substitutions)
    print "Finished. Wrote improved submission to :", outfile_name
    print


