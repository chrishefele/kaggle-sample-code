
UNIGRAMS_FILE = '../data/train_ngrams_1+1.txt'

class Vocabulary:

    # Note: These class variables are shared by all instances to save memory 
    file_loaded  = None
    _word_to_id  = None
    _id_to_word  = None

    def __init__(self, unigrams_fname=UNIGRAMS_FILE):

        if not Vocabulary.file_loaded: 
            self.load_file(unigrams_fname)
            Vocabulary.file_loaded = unigrams_fname
        else: 
            print 'NOT loading vocabulary from', unigrams_fname, 
            print 'because', Vocabulary.file_loaded, 'is already loaded'

    def load_file(self, unigrams_fname):
        print "Loading vocabulary from:", unigrams_fname
        word_ids = 0
        Vocabulary._word_to_id  = {}
        Vocabulary._id_to_word  = {}
        unigrams_file = open(unigrams_fname, 'rb')
        for line in unigrams_file:
            tokens = line.rstrip().split()
            assert len(tokens) == 2 
            count = int(tokens[0])
            word  =     tokens[1]   # single word = unigram
            word_ids += 1
            word_id = word_ids
            Vocabulary._word_to_id[word   ] = word_id
            Vocabulary._id_to_word[word_id] = word 
        print word_ids,"vocabulary words loaded from:", unigrams_fname

    def __contains__(self, word):
        return word in Vocabulary._word_to_id

    def word_to_id(self, word):
        # return   Vocabulary._word_to_id[word]
        return     Vocabulary._word_to_id.get(word, 0)

    def id_to_word(self, word_id):
        # return   Vocabulary._id_to_word[word_id]
        return     Vocabulary._id_to_word.get(word_id, '')


if __name__ == '__main__':
    v = Vocabulary()
    print 'the' in v
    print v.word_to_id('the')
    print v.id_to_word(1)

