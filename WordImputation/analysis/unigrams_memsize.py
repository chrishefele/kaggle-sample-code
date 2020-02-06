
word_to_int = {}
int_to_word = {}

unigrams = open('../data/train_ngrams_1+1.txt','r')
for n, line in enumerate(unigrams):
    tokens = line.rstrip().split()
    assert len(tokens)==2
    count = int(tokens[0])
    word  =     tokens[1]
    word_to_int[word] = n
    int_to_word[   n] = word

unigrams.close()

