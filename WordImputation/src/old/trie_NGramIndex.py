import sys
import marisa_trie  # memory-efficient implementation of trie data structure
import time

data_format = "<i"
WORD_SEP = "`"

class NGramIndex:

    def __init__(self, ngram_file, **kwargs):
        self.build_index(ngram_file, **kwargs)
    
    def build_index(self, ngram_file, **kwargs):
        data = self.data_generator(ngram_file, **kwargs)
        self.trie = marisa_trie.RecordTrie(data_format, data)

    def data_generator(self, ngram_file, max_lines=0, min_count=0):
        fin = open(ngram_file,'r')
        for n_lines, line in enumerate(fin):
            tokens = line.rstrip().split()
            count = int(tokens[0])
            if max_lines and n_lines > max_lines:
                break
            if count < min_count:
                break
            words = WORD_SEP.join(tokens[1:])  
            words_start = words
            words = words.decode("utf-8")
            if words_start != words.encode("utf-8"):
                print n_lines, "reencoded NOT EQUAL"
            # print n_lines, words, type(words)
            if n_lines % 100000 == 0:
                print "\r", float(n_lines)/1000000,"million",
                sys.stdout.flush()
            yield (words, (count,))
        fin.close()

    # pass in a list of words, make a string, search trie, return a list of next words
    def match_keys(self, s):
        return self.trie.keys(s)

    # pass in a list of words, make a string, search trie, return list of next words & counts
    def match_items(self, s):
        return self.trie.items(s)


if __name__ == '__main__':
    #trigrams = NGramIndex('../data/3_grams.txt', max_lines=1000000)
    trigrams = NGramIndex('../data/3_grams.txt', min_count = 20)
    print trigrams.match_keys( u"he`said`")
    print trigrams.match_keys( u"humbugerooski`said`")
    print trigrams.match_items(u"he`said`")
    t0 = time.time()
    for i in range(10000):
        result = trigrams.match_items(u"he`said`")
    print time.time() - t0, "sec per 10000"
        


