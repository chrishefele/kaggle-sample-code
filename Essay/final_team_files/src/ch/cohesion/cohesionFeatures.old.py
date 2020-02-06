# cohesionFeatures.py 
# 3/19/2012 by Chris Hefele
#
# This code generates essay cohesion features by performing an LSA on the group
# of sentences in each essay set, then determining the distance between
# adjacent sentences in each essay in the LSA space.  
# The average distance between all pairs of sentences is also
# computed, which reflects the average distance between sentences if
# they were randomly permuted. A ratio of the average adjacent 
# sentence distance to the average all-sentence distance is also  
# computed, which reflects how 'non-random' the arragnement
# of sentences is. (i.e. how much similar ideas are grouped). 
#

import sys
import string 
import numpy
import nltk # natural language toolkit
import gensim

numpy.random.seed(1234567)  # Gensim uses a stochastic SVD for LSA, so fix the 
                            # seed for consistent SVD results between runs 

def printableText(text):
    return ''.join(filter(lambda x:x in string.printable, text))

def rmStopWords(text):
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = nltk.wordpunct_tokenize(text)
    nostop = [t for t in tokens if t not in stopwords]
    return ' '.join(nostop)

def lowercase(text):
    return text.lower()

class WordStemmer:  # stemming is used to count words using common suffixes 
    def __init__(self):
        self.stemmer   = nltk.PorterStemmer()
    def stemWords(text):
        tokens = nltk.wordpunct_tokenize(text)
        return ' '.join([ self.stemmer.stem(t).lower() for t in tokens ])

def printStatus(n):
    PRINT_MOD = 100 
    if n % PRINT_MOD == 0:
        print n,
        sys.stdout.flush()

class EssayDataFile:
    def __init__(self, fnames):
        self.essay_data = [essay_datum for essay_datum in self._parseEssays(fnames)] 
        # [ (essay_id, essay_set, [['sent1word1', 'sent1word2',...], ['sent2word1', 'sent2word2'...]...]), ... ]

    def essayData(self):
        return self.essay_data

    def _parseEssays(self, fnames, stopwords=True, stemwords=False, lower=True ):
        sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        # word_tokenizer = lambda s: s.split()
        word_tokenizer = nltk.wordpunct_tokenize
        word_stemmer = WordStemmer()

        for fname in fnames:
            print "\nParsing essay file:", fname
            print "essay_id:",
            sys.stdout.flush()
            fin = open(fname,'r')
            header = fin.readline().split('\t')
            for line in fin:
                fields = line.split('\t')
                essay_id, essay_set, essay_raw = int(fields[0]), int(fields[1]), fields[2]
                essay = printableText(essay_raw)
                if lower:
                    essay = lowercase(essay)
                if stopwords:
                    essay = rmStopWords(essay)
                if stemwords:
                    essay = word_stemmer.stemWords(essay)
                essay_sentences       = sent_tokenizer.tokenize(essay)
                essay_sentences_words = [word_tokenizer(s) for s in essay_sentences]  
                yield (essay_id, essay_set, essay_sentences_words)
                printStatus(essay_id)
            fin.close()
            print 


def concatEssaysSentences(essays):
    return [sent for essay in essays for sent in essay ]


class LSA_Engine:
    def __init__(self, essay_train, num_topics):
        self.trainLSA(essay_train, num_topics)

    def trainLSA(self, essay_train, num_topics):
        #if len(essay_train) == 1:
        #    essay_train = [essay_train[0], essay_train[0][:-1]]  # TODO: ?HACK to avoid crash when only 1 sentence
        self.dictionary = gensim.corpora.Dictionary(essay_train) # maps words to integer column id's 
        # self.dictionary.filter_extremes() # tested this, but no impact; also creates nan's (e.g. essay 10022) 
        corpus          = [self.dictionary.doc2bow(s) for s in essay_train] # sentences --> sparse-matrix vectors 
        self.model_tfidf= gensim.models.TfidfModel(corpus)      
        corpus_tfidf    = self.model_tfidf[corpus]               # map to word freqs using tfidf before LSA
        self.model_lsi  = gensim.models.lsimodel.LsiModel(corpus_tfidf, id2word=self.dictionary, num_topics=num_topics)
        self.num_topics = num_topics

    def scoreEssay(self, essay, **kwargs):
        essay_corpus = [self.dictionary.doc2bow(essay_sent) for essay_sent in essay] 
        essay_corpus_mapped = self.model_lsi[ self.model_tfidf[ essay_corpus ]]    
        index = gensim.similarities.MatrixSimilarity( essay_corpus_mapped ) 
        sent_sims_matrix = numpy.vstack([numpy.array(sims) for sims in index])
        nrow, ncol = sent_sims_matrix.shape
        assert nrow == ncol
        if nrow > 1:
            sim_adjacent_mean   = numpy.mean(   sent_sims_matrix.diagonal(1)) # off-diagonal by 1
            sim_adjacent_median = numpy.median( sent_sims_matrix.diagonal(1)) # off-diagonal by 1
            sim_adjacent_sum    = numpy.sum(    sent_sims_matrix.diagonal(1)) # off-diagonal by 1
            sim_adjacent_std    = numpy.std(    sent_sims_matrix.diagonal(1)) # off-diagonal by 1
            dissim_adjacent_sum = numpy.sum(1.- sent_sims_matrix.diagonal(1)) # off-diagonal by 1
            sim_all_sum         = sent_sims_matrix.sum() - sent_sims_matrix.diagonal().sum() 
            dissim_matrix       = 1.-sent_sims_matrix
            dissim_all_sum      = dissim_matrix.sum() - dissim_matrix.diagonal().sum() 
            sim_all_mean        = sim_all_sum / float(nrow*ncol - nrow) # off-diagonal elements mean 
            sim_ratio           = sim_adjacent_mean / sim_all_mean
        else:   # edge case:  only 1 sentence in the essay, so no adjacent sentences 
            sim_adjacent_mean   = 0.0
            sim_adjacent_median = 0.0
            sim_adjacent_sum    = 0.0
            sim_adjacent_std    = 0.0
            dissim_adjacent_sum = 0.0
            sim_all_sum         = 0.0
            dissim_all_sum      = 0.0
            sim_all_mean        = 0.0
            sim_ratio           = 1.0
        v = {}
        suffix = '_%04i' % self.num_topics
        v['CH_cohesionAdjMean'+suffix]          = sim_adjacent_mean
        v['CH_cohesionAdjMedian'+suffix]        = sim_adjacent_median
        # v['CH_cohesionAdjSum'+suffix]           = sim_adjacent_sum  # too similar to length?
        # v['CH_cohesionAdjStd'+suffix]           = sim_adjacent_std  # not really strong 
        v['CH_cohesionAdjSumDissim'+suffix]     = dissim_adjacent_sum
        # v['CH_cohesionAllSum'+suffix]           = sim_all_sum       # too similar to length?
        v['CH_cohesionAllSumDissim'+suffix]     = dissim_all_sum
        v['CH_cohesionAllMean'+suffix]          = sim_all_mean
        v['CH_cohesionAdjAllMeanRatio'+suffix]  = sim_ratio
        return v

def printEssayStats(essay_data):
    word_counts = {}
    sentence_counts = {}
    for essay_id, essay_set, essay_sentence_words in essay_data:
        for sentence in essay_sentence_words:
            sentence_counts.setdefault(essay_set, 0) 
            sentence_counts[essay_set] += 1
            for word in sentence:
                word_counts.setdefault(essay_set,{})
                word_counts[essay_set].setdefault(word, 0) 
                word_counts[essay_set][word] += 1 
    print 
    for essay_set in word_counts:
        print "Essay_set:", essay_set, 
        print "UniqWords:", len(word_counts[essay_set]), 
        print "Sentences:", sentence_counts[essay_set]
    print
    sys.stdout.flush()

def keyValCSV(d):
    key_csv = ','.join([str(key) for key,val in sorted(d.items())])
    val_csv = ','.join([str(val) for key,val in sorted(d.items())])
    return key_csv, val_csv

def writeFeatures(num_topics, ftrain, ftest, fout):
    print "Generating cohesion features"
    print "Number of topics   :", num_topics
    print "LSA training   file:", ftrain
    print "Feature essay  file:", ftest
    print "Feature output file:", fout

    # read the essay data file & group the essays by essay_set
    eset_essays    = {}  
    edf = EssayDataFile([ftrain])
    for essay_id, essay_set, essay_parsed in edf.essayData():
        eset_essays.setdefault(essay_set,[])
        eset_essays[essay_set].append(essay_parsed)
    # eset_essays = { essay_set:[essay,...],... }  essay=[sentence,...] sentence=['word',...]
    printEssayStats(edf.essayData())

    # calculate the LSA model for each essay_set seperately
    eset_lsa_engine = {}
    for essay_set, essays in eset_essays.iteritems():
        for ntop in num_topics:
            print "Calculating LSA on essay_set:", essay_set, "Number of topics:", ntop
            sys.stdout.flush()
            eset_lsa_engine.setdefault(essay_set,[])
            eset_lsa_engine[essay_set].append(LSA_Engine(concatEssaysSentences(essays), ntop))

    # loop through the test file, calculate features & write them out
    if ftrain==ftest:
        edf2 = edf  # save time by not rereading if it's the same file
    else:
        edf2 = EssayDataFile([ftest])
    print "Generating features using:", ftest
    print "essay_id:",
    header_done = False
    fout_file = open(fout,'w')
    for essay_id, essay_set, essay_parsed in edf2.essayData():
        scores = {}
        for engine in eset_lsa_engine[essay_set]:
            new_scores = engine.scoreEssay(essay_parsed)
            scores = dict( scores.items() + new_scores.items() )
        #self_scores = LSA_Engine(essay_parsed, num_topics).scoreEssay(essay_parsed) # TODO?
        labels = { 'essay_id':essay_id, 'essay_set':essay_set }
        cols   = dict(labels.items() + scores.items())
        key_csv, val_csv = keyValCSV(cols)
        if not header_done:
            fout_file.write(key_csv+"\n")
            header_done = True
        fout_file.write(val_csv+'\n')
        printStatus(essay_id)
    fout_file.close()
    print "\nDone. Features written to:", fout


def process_command_line():
    if len(sys.argv) != 5:
        print "usage: python cohesionFeatures.py <num_LSA_topics> <LSA_train_essays> <essays_for_features> <features_output>"
    else:
        num_topics      = [ int(i) for i in sys.argv[1].split(',') ] # e.g.  1,2,4,8,16 (no spaces)
        f_LSA_train     = sys.argv[2]
        f_feats_essays  = sys.argv[3]
        f_feats_out     = sys.argv[4]
        writeFeatures(num_topics, f_LSA_train, f_feats_essays, f_feats_out)

def main():
    process_command_line()

main()

