import csv
 
TEST_FILE       = '../download/test_v2.txt'

test_file  = csv.reader(open(TEST_FILE,       'rb'))
header = test_file.next()

for line in test_file:
    sentence_id, sentence = line
    sentence_id = int(sentence_id)
    words = sentence.rstrip().split()
    print ' '.join(words)
