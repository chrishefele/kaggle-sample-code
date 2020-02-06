# matches sentences in the test set to likely unique sentences in the training set
# There are about 3600 unique matches out of 300K, so about a 1% match rate,
# which would yield about a 0.05 advantage (something, but not much)
#
# all matches (including non-unique matches, 
# (i.e. multiple train sentences match a test sentence) are about 10%,
# and tend to be shorter (e.g. 4-5 words).

import csv
from collections import defaultdict

TEST_FILE       = '../download/test_v2.txt'
TRAIN_FILE      = '../download/train_v2.txt'

def test_sentence_reader():
    test_file  = csv.reader(open(TEST_FILE, 'rb'))
    header = test_file.next()
    for line in test_file:
        sentence_id, sentence = line
        sentence_id = int(sentence_id)
        yield sentence

def train_sentence_reader():
    train_file = open(TRAIN_FILE, 'rb')
    for n, line in enumerate(train_file, start=1):
        # if n > 100000: break
        yield line.rstrip()


def main():

    test_sentences = set()
    test_sentence_delword = defaultdict(list)

    for sentence in test_sentence_reader():
        test_sentences.add(sentence)

    print 
    for line_num, sentence in enumerate(train_sentence_reader(), start=1):
        if line_num % 100000 == 0:
            print "%iK" % (line_num/1000,) , 
        words = sentence.split()
        for del_posn in range(1, len(words)-1):
            del_word    = words[del_posn]
            left_words  = words[            :del_posn] 
            right_words = words[(del_posn+1):        ]
            del_sentence = ' '.join(left_words + right_words)

            if del_sentence in test_sentences:
                test_sentence_delword[del_sentence].append(del_word)
                if False:
                    ctr_word = ['[[', del_word,']]']
                    print ' '.join(left_words + ctr_word + right_words),
                    print line_num, 
                    print len(left_words), len(right_words), len(words)
    
    print 
    for sentence in test_sentence_delword:
        del_words = test_sentence_delword[sentence] 
        print "SENTENCE      :", sentence
        print "INSERT_WORDS  :", del_words
        print "N_INSERT_WORDS:", len(del_words),
        print "N_SENT_WORDS  :", len(sentence.split())
        print 

main()

