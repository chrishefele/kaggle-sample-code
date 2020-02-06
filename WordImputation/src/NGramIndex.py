import sys, time
import numpy
import itertools
from Vocabulary import Vocabulary

class NGramIndex:
    """ 
        This class maintains an index of information about n-grams using a 
        table of sorted hashes.  It has two modes of operation, depending
        on whether or not 'index_insert_word' is True or False:

        * If 'index_insert_word' is true, then for an n-gram, 
          n-1 words are used as the 'context' i.e. a table is kept with rows:
            <context-ngram-hash> <context-ngram-count> <insert-word-id>
          where <insert-word> is the word that completes the n-gram,
          derived from the insert_word_posn in the ngram.

        * If 'index_insert_word' is False, then for an n-gram, 
          all n words are used, i.e. a table is kept with rows:
            <ngram-hash> <ngram-count> 

        The tables are sorted by the hash, and ngram information
        is retrieved by doing a binary search on the ngram hashes to 
        find the appropriate row(s) with the other ngram info.
        This is approach is MUCH more memory efficient than an approach
        that uses a python dictionary (by a factor of about 10).

    """

    PRINT_MOD = 100000 

    def __init__(self, ngram_file, insert_word_posn, index_insert_words, min_count):
        
        print "\nNGramIndex: Initializing a new index" 

        self.index_insert_words = index_insert_words
        self.counts_total    = 0
        self.num_uniq_ngrams = 0 
        self.vocab = Vocabulary()

        print "Now examining ngram counts in", ngram_file
        max_lines = self.ngram_file_mincount_line(ngram_file, min_count)
        print "For a min ngram count of ", min_count,
        print "need to read", max_lines, "ngrams from", ngram_file

        self.ngram_hash   = numpy.zeros(max_lines, dtype=numpy.int64)
        self.ngram_count  = numpy.zeros(max_lines, dtype=numpy.int32)
        if index_insert_words:
            self.ngram_gapword = numpy.zeros(max_lines, dtype=numpy.int32)

        self.build_index(ngram_file, insert_word_posn, index_insert_words, 
                         max_lines, min_count)


    def ngram_file_mincount_line(self, fname, min_count):
        fin = open(fname)
        for line_num, line in enumerate(fin):
            # Each ngram file contains lines with the ngram_count & ngram tokens,
            # one ngram per line, with lines sorted in descending order by count.
            count = int(line.split()[0])
            if count < min_count:
                break
        fin.close()
        return  line_num

    def hash_words(self, word_list):
        return hash(' '.join(word_list))

    def build_index(self,   ngram_file, insert_word_posn, index_insert_words, 
                            max_lines, min_count):
        ix = 0
        ngram_counts = self.read_ngram_counts( ngram_file, max_lines=max_lines, 
                                                           min_count=min_count )
        for ngram, count in ngram_counts:

            if index_insert_words:
                assert 0 <= insert_word_posn < len(ngram)-1 
                # NOTE Slightly tricky indexing issue: By convention,
                # insert_word_position usually points at the word before 
                # the assumed gap/deleted word.  It can't point at the deleted 
                # word directly, because the deleted word is assumed gone. 
                # But when indexing ngrams that *do* include the 
                # "insert word" that will be deleted, one *can* point to it; 
                # it's in the (insert_word_posn+1) position. 
                insert_word   = ngram[ (insert_word_posn+1)]
                context_words = ngram[:(insert_word_posn+1)] + ngram[(insert_word_posn+1+1):]
                self.ngram_hash[ ix]  = self.hash_words(context_words)
                self.ngram_count[ix]  = count
                self.ngram_gapword[ix] = self.vocab.word_to_id(insert_word)
                # DEBUG prints
                if False:
                    print ix, context_words, self.ngram_hash[ ix], '->', 
                    print insert_word, self.ngram_gapword[ix], 
                    print 'count:', self.ngram_count[ix] 
            else:
                self.ngram_hash[ ix]  = self.hash_words(ngram)
                self.ngram_count[ix]  = count
                # DEBUG prints
                if False:
                    print ix, ngram, self.ngram_hash[ ix], 
                    print 'count:', self.ngram_count[ix] 

            ix += 1 
            self.counts_total += count
            self.num_uniq_ngrams += 1 

        print "Sorting the index by ngram hash"
        sort_order = self.ngram_hash.argsort()
        self.ngram_hash  = self.ngram_hash[ sort_order]
        self.ngram_count = self.ngram_count[sort_order]
        if index_insert_words:
            self.ngram_gapword = self.ngram_gapword[sort_order]
        pass

    def read_ngram_counts(self, ngram_file, max_lines=None, min_count=None):
        print "Reading n-grams from:", ngram_file
        fin = open(ngram_file,'r')
        for line_num, line in enumerate(fin):
            tokens = line.rstrip().split()
            count  = int(tokens[0])
            ngram  = tokens[1:]
            self.print_status(line_num)
            if max_lines and line_num >= max_lines - 1:
                print "\nStopped: reached file   max_lines limit of:", max_lines
                print "Read", line_num,"lines."
                break
            if min_count and count < min_count: 
                print "\nStopped: reached n-gram min_count limit of", min_count
                print "Read", line_num,"lines."
                break
            yield (ngram, count)
        fin.close()
        print self.counts_total, "total n-grams,", 
        print self.num_uniq_ngrams, "unique",
        print "(%6.2f%%)" % (100.*self.num_uniq_ngrams/self.counts_total)

    def print_status(self, line_num):
        # during lengthy file read, print a '.' after every reading PRINT_MOD lines
        if line_num % NGramIndex.PRINT_MOD == 0:
            sys.stdout.write('.')
            sys.stdout.flush()

    # @profile # for line_profiler
    def insert_word_suggestions(self, context_words):
        assert self.index_insert_words == True
        suggestions = []
        h = self.hash_words(context_words)
        ix = self.ngram_hash.searchsorted(h)
        while 0 <= ix < len(self.ngram_hash) and self.ngram_hash[ix] == h : 
            word_id = self.ngram_gapword[ix]
            word = self.vocab.id_to_word(word_id) 
            count   =  self.ngram_count[ix]
            suggestions.append((word, count)) 
            ix += 1
        return suggestions

    #def get_count_cased(self, ngram_words):
    def get_count(self, ngram_words):
        assert self.index_insert_words == False
        h  = self.hash_words(ngram_words)
        ix = self.ngram_hash.searchsorted(h) 
        found =  0 <= ix < len(self.ngram_hash)  and  self.ngram_hash[ix] == h
        if not found:
            return 0  
        else:
            return self.ngram_count[ix]

    """
    def lowercased_ngrams(self, ngram_words):
        # create up to 2^N ngrams by lowercasing (if possible) each n-gram 
        # word that looks like a title (starts with uppercase & not all caps)
        maybe_lower = lambda word: (word,) if not word.istitle() else (word, word.lower())
        ngram_words_lower = (maybe_lower(ngram_word) for ngram_word in ngram_words)
        return itertools.product(*ngram_words_lower)

    def insert_word_suggestions(self, context_words):
        # return self.insert_word_suggestions_cased(context_words)
        suggestions = []
        for ngram in self.lowercased_ngrams(context_words):
            suggestions.extend( self.insert_word_suggestions_cased(ngram) )
        return suggestions

    def get_count(self, ngram_words):
        # return self.get_count_cased(ngram_words)
        return sum(self.get_count_cased(ngram) for ngram in self.lowercased_ngrams(ngram_words) )
    """ 

if __name__ == '__main__':

    trigrams = NGramIndex('../data/3_grams.txt', 1, True, 20)

    #test_ngram_wordlist = ['hello', 'THERE','How','Are']
    #print list(trigrams.lowercased_ngrams(test_ngram_wordlist))

    context_words = ["he","said"]
    w1, w2 = context_words
    candidates = [ (count, word) for word, count in \
                   trigrams.insert_word_suggestions(context_words) ]
    candidates.sort(reverse=True)
    print 
    for candidate in candidates:
        print w1, candidate, w2
    print 

    t0 = time.time()
    for i in range(10000):
        result = trigrams.insert_word_suggestions(context_words)
    print time.time() - t0, "sec per 10000"

