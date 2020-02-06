import csv
from SkipNoSkipModel import SkipNoSkipModel
from BackoffModel import BackoffModel
 
TEST_FILE       = '../download/test_v2.txt'
SUBMISSION_FILE = 'submission.csv'
PRINT_MOD       = 1000  # 10000    

# MODEL PARAMETERS below (tuned using the holdout set)
                            
MIN_COUNT       = 3     # Don't include n-grams with <MIN_COUNT occurences 
REGULARIZATION  = 1     # N-gram smoothing parameter; use 1 for best results
best_model_masks = ('1101','1011', '101' )  # ngram masks for backoff model

print '\n*** Word Imputation Contest - Submission generator ***\n' 
print "min_count      :", MIN_COUNT
print "regularization :", REGULARIZATION
print "model masks    :", best_model_masks
print

model = BackoffModel(masks=best_model_masks, min_count=MIN_COUNT)

print 'Finished initializing model.\n'
print 'Reading from:', TEST_FILE
print 'Writing to  :', SUBMISSION_FILE
print 

test_file  = csv.reader(open(TEST_FILE,       'rb'))
submission = csv.writer(open(SUBMISSION_FILE, 'wb'), quoting=csv.QUOTE_NONNUMERIC)

header = test_file.next()
submission.writerow( header )

for line in test_file:
    sentence_id, sentence = line
    sentence_id = int(sentence_id)
    words = sentence.rstrip().split()
    sentence_prediction = model.best_sentence(words, REGULARIZATION)
    submission.writerow( (sentence_id, sentence_prediction) ) 
    if sentence_id % PRINT_MOD == 0:
        print 'Processed line:', sentence_id

# model.save_cache()
print "\nFinished. Wrote submission to:", SUBMISSION_FILE,"\n"

