# xfeatures.py
# 1/25/2012 by Chris Hefele
#
# usage: python xfeatures.py <infile> <outfile> 
#
# This program takes each essay in the input dataset file & creates a number of features
# based on style/readability statistics, spelling, and the anonymization substitutions.
#

import subprocess
import sys
import zlib
import random
import string 
import math 
import numpy
import nltk # natural language toolkit

RAND_SEED= 1234567
random.seed(RAND_SEED)

#ARGUMENT_PHRASES = '../texts/argument_phrases.txt'  # phrases to spot indicating new points / ideas
#PROMPTS_DIR      = '../texts/'                      # essay prompts / questions 
ARGUMENT_PHRASES = '../../../data/argument_phrases.txt'  # phrases to spot indicating new points / ideas
PROMPTS_DIR      = '../../../data/prompts/'              # essay prompts / questions 

PRINT_STATUS_MOD = 20


def styleStats(essay_text, **kwargs):

    # define some convenience functions
    def rmParens(s):
        return s.replace('(','').replace(')','')
    def rmPercent(s):
        return s.replace('%','')
    def rmEllipsis(s):
        return s.replace('...','   ')

    # clean up some corner cases
    if essay_text[0]=='"' and essay_text[-1]=='"':  # remove any quoting
        essay_text = essay_text[1:-1]  

    if not essay_text[0].isupper():     # 'style' must have at least 1 capital letter
        essay_text = essay_text[0].upper() + essay_text[1:] 
    if essay_text[0]==' ' and not essay_text[1].isupper():     # *** special case for essay 22156, no caps & leading space
        essay_text = essay_text[0] + essay_text[1].upper() + essay_text[2:] 

    essay_text = rmEllipsis(essay_text) # "Ya... go." crashes 'style', so remove ellipsis
    essay_text = essay_text + '.'       # 'style' crashes without at least 1 period 

    # call Linux 'style' command to calculate readability statistics of essay text, then parse its output
    process = subprocess.Popen(['style'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    styleOut , styleErr = process.communicate(essay_text)
    e = [line.split() for line in styleOut.split('\n')]
    v = {}  
    v["Kincaid"]            = float(e[ 1][1])
    v["ARI"]                = float(e[ 2][1])
    v["ColemanLiau"]        = float(e[ 3][1])
    v["FleschIndex"]        = float(e[ 4][2].replace('/100',''))
    v["FogIndex"]           = float(e[ 5][2])
    v["Lix"]                = float(e[ 6][1]) 
    v["schoolYr"]           = int(  e[ 6][-1]) 
    v["SMOGGrading"]        = float(e[ 7][1])
    v["nchars"]             = int(  e[ 9][0])
    v["nwords"]             = int(  e[10][0])
    v["logNwords"]          = math.log(int(  e[10][0]))
    v["avgWordLen"]         = float(e[10][4])
    v["avgWordSyl"]         = float(e[10][7])
    v["nSentences"]         = int(  e[11][0])
    nSentences              = int(  e[11][0])
    v["avgSentWords"]       = float(e[11][4])
    v["pctShortSent"]       = int(rmPercent(e[12][0]))
    v["pctLongSent"]        = int(rmPercent(e[13][0]))
    v["pctQuestions"]       = int(rmPercent(e[15][0]))
    v["pctPassiveSent"]     = int(rmPercent(e[16][0]))
    v["longestSentWords"]   = int(  e[17][2])
    v["shortestSentWords"]  = int(  e[17][9])
    v["tobeVerb"]           = int(rmParens( e[20][2]))
    v["auxVerb"]            = int(rmParens( e[20][4]))
    v["pctConjunctions"]    = int(rmPercent(e[22][1]))
    v["pctPronouns"]        = int(rmPercent(e[22][4]))
    v["pctPrepositions"]    = int(rmPercent(e[22][7]))
    v["pctNominalizations"] = int(rmPercent(e[23][1]))

    v["sentStartPronoun"]   = int(rmParens( e[25][1]))
    v["sentStartInterPronoun"] = int(rmParens(e[25][4]))
    v["sentStartArticle"]   = int(rmParens( e[25][6]))
    v["sentStartSubConj"]   = int(rmParens( e[26][2]))
    v["sentStartConj"]      = int(rmParens( e[26][4]))
    v["sentStartPrep"]      = int(rmParens( e[26][6]))
    
    def pctSent(n):
        return float(n) / nSentences
    v["pctSentStartPronoun"]   = pctSent( v["sentStartPronoun"] )
    v["pctSentStartInterPronoun"] = pctSent( v["sentStartInterPronoun"] )
    v["pctSentStartArticle"]   = pctSent( v["sentStartArticle"] )
    v["pctSentStartSubConj"]   = pctSent( v["sentStartSubConj"] )  
    v["pctSentStartConj"]      = pctSent( v["sentStartConj"] )       
    v["pctSentStartPrep"]      = pctSent( v["sentStartPrep"] )     

    return v


def rmStopWords(text):
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = nltk.word_tokenize(text)
    nostop = [t.lower() for t in tokens if t.lower() not in stopwords]
    return ' '.join(nostop)

def miscStyleStats(essay_text, **kwargs):
    # generate some additional stylistic features, not computed by the 'style' command 
    v = {}
    nw                                  =  len(    essay_text.split() ) # num words 
    nuw                                 =  len(set(essay_text.split())) # num unique words
    v["numUniqWords"]                   =  nuw
    v["logNumUniqWords"]                =        math.log(nuw)
    v["numUniqWordsXlogNumUniqWords"]   =  nuw * math.log(nuw)
    v["pctUniqWords"]                   =  int(100.0*nuw / nw)
    v["nCharsUniqWords"]                =  len(' '.join(set(essay_text.split())))
    v["nCharsAllWords"]                 =  len(' '.join(    essay_text.split()))
    v["nWordsXlogNWords"]               =  nw * math.log(nw)
    return v

def anonStats(essay_text, **kwargs):
    tags = ["PERSON", "ORGANIZATION", "LOCATION", "DATE", "TIME", "MONEY", \
            "PERCENT", "MONTH", "EMAIL", "NUM", "CAPS", "DR", "CITY", "STATE" ] 
    nwords = len(essay_text.split())
    v = {}
    for tag in tags:
        v['n'  +tag] =       essay_text.count('@'+tag)
        v['pct'+tag] = float(essay_text.count('@'+tag)) / nwords
    #v['nATSIGN']     =       essay_text.count('@')
    #v['pctATSIGN']   = float(essay_text.count('@')) / nwords
    return v

def spellingStats(essay_text, **kwargs):
    # create spelling statistics by calling 'spell' to count spelling errors
    process = subprocess.Popen(['spell'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    spellOut , spellErr = process.communicate(essay_text)
    sp_errs = spellOut.split('\n')
    nwords  = len(    essay_text.split()) 
    nuwords = len(set(essay_text.split())) 
    v = {}
    v["nSpellErrs"]         =        len(    sp_errs )
    v["nUniqSpellErrs"]     =        len(set(sp_errs))
    v["pctSpellErrs"]       =  float(len(    sp_errs))  / len(    essay_text.split())
    v["pctUniqSpellErrs"]   =  float(len(set(sp_errs))) / len(set(essay_text.split()))
    return v

def shuffleWords(essay_text, **kwargs):
    words = essay_text.split(' ')
    random.shuffle(words)
    return ' '.join(words)

def gzLength(txt): 
    return len(zlib.compress(txt,9))

def gzRatio(txt): 
    return min(1.0, float(len(zlib.compress(txt,9))) / len(txt) )

def gzRatioUniq(txt): 
    words = txt.split()
    no_word_redundancy_ratio =  float(len(set(words))) / len(words)
    return gzRatio(txt) / no_word_redundancy_ratio 

def gzipStats(essay_text, **kwargs):
    essay_stop = rmStopWords(essay_text)
    v = {}
    v["gzipLength"]         = gzLength(   essay_text)
    v["gzipLengthNoStop"]   = gzLength(   essay_stop) 
    v["gzipRatio"]          = gzRatio(    essay_text) # char-level compression ratio
    v["gzipRatioUniq"]      = gzRatioUniq(essay_text) # compression vs word-redundancies removed
    # gzipRatioWordShuf capture additional compression ratio possible due to sequences of words 
    v["gzipRatioWordShuf"]       = gzRatio(essay_text) / gzRatio(shuffleWords(essay_text)) 
    v["gzipRatioWordShufNoStop"] = gzRatio(essay_stop) / gzRatio(shuffleWords(essay_stop)) 
    return v 

def uniqCounts(items):
    counts = {}
    for item in items:
        if item not in counts:
            counts[item] = 0
        counts[item] += 1
    return counts

def normUniqCounts(uniq_counts):
    return math.sqrt(sum([pow(uniq_counts[k],2)  for k in uniq_counts]))

def wordListCosine(w1, w2):
    w1count = uniqCounts(w1)
    w2count = uniqCounts(w2)
    dot_prod = sum([w1count[k]*w2count[k] for k in w1count if k in w2count])
    cosine = float(dot_prod) / (normUniqCounts(w1count)*normUniqCounts(w2count))
    return cosine

class PromptStats:
    def __init__(self):
        self.eset_prompt       = {}
        self.eset_prompt_words = {}
        for eset in [1,2,3,4,5,6,7,8]: # read each essay set prompt
            prompt_lines = open(PROMPTS_DIR+'prompt'+str(eset)+'.txt','r').readlines()
            prompt = ' '.join(prompt_lines)
            self.eset_prompt[eset] = prompt
            self.eset_prompt_words[eset] = prompt.split()

    def promptStats(self, essay_text, **kwargs):
        eset = int(kwargs['essay_set'])
        etext       = essay_text
        etext_words = etext.split()
        prompt      = self.eset_prompt[eset]
        prompt_words= self.eset_prompt_words[eset]
        v = {}
        v['gzipRatioPromptDivPromptEssay'    ] = gzRatio(    etext) / gzRatio(    etext+prompt)
        v['gzipRatioUniqPromptDivPromptEssay'] = gzRatioUniq(etext) / gzRatioUniq(etext+prompt)
        v['cosinePromptEssayWordCounts'      ] = wordListCosine(    etext_words,      prompt_words)
        v['cosinePromptEssayUniqWords'       ] = wordListCosine(set(etext_words), set(prompt_words))
        return v 

def miscStats(essay_text, **kwargs):
    nwords = len(essay_text.split())
    v = {}
    v['nQMark3'  ] =       essay_text.count('???')
    v['pctQMark3'] = float(essay_text.count('???')) / nwords
    return v

def randStats(essay_text, **kwargs):
    v = {}
    for i in xrange(5):
        tag = '%02i' % i 
        v['randomNormal'   +tag] = numpy.random.normal()
        v['randomLogNormal'+tag] = numpy.random.lognormal()
    return v

def vocabStats(essay_text, **kwargs):
    # remove nonprintable chars
    essay = ''.join(filter(lambda x:x in string.printable, essay_text)) 
    words = [ word.strip().lower() for word in essay.split() ] 

    wordCounts  = uniqCounts(words)
    countCounts = uniqCounts(wordCounts.values())
    nWords      = len(words) + 1 # hack: +1 to avoid /0 if all essay words are unique
    nUniqWords  = len(wordCounts)
    nSingleWords = countCounts[1] if 1 in countCounts else 0  # single appearence words

    # Vocabulary size estimators are based on equations 2.2, 2.3, 2.12 & 2.14 in 
    # "Estimating the Number of Classes via Sample Coverage" by Chao & Lee
    coverage = (1. - float(nSingleWords)/nWords)
    vocabSize1 = nUniqWords/coverage  
    gamma2 = max(0.,  float(vocabSize1) / (nWords*(nWords-1.)-1.) * \
                      sum([i*(i-1)*countCounts[i] for i in countCounts])  \
                ) 
    vocabSize2 = nUniqWords/coverage + nWords*(1.-coverage)/coverage*gamma2

    v = {}
    v['vocabSizeEst1']  = vocabSize1
    v['vocabSizeEst2']  = vocabSize2
    v['vocabSizeEssay'] = nUniqWords
    v['vocabSingleWords'] = nSingleWords
    return v

class PhraseSpotter:
    def __init__(self, phrase_list=[], phrase_file=''):
        if phrase_file:
            print "Reading phrases to spot from:", phrase_file
            file_phrases = [line.strip().lower() for line in open(phrase_file,'r') if line.strip() != '' and '#' not in line]
        else:
            file_phrases = []
        self.phrases = set(file_phrases + phrase_list)

    def phraseHits(self, essay, **kwargs):
        essay_clean = ' '.join([wrd.strip() for wrd in essay.lower().split() ])
        hits = sum([essay_clean.count(phrase) for phrase in self.phrases])
        return hits

class SubjModalAuxVerbs(PhraseSpotter):
    def subjModalAuxVerbStats(self, essay, **kwargs):
        hits = self.phraseHits(essay)
        words = len(essay.split())
        v = {}
        v['subjModalAuxVerbsCount'] = hits
        v['subjModalAuxVerbsPct'  ] = float(hits) / words 
        return v

class ArgumentPhrases(PhraseSpotter):
    def argPhraseStats(self, essay, **kwargs):
        hits = self.phraseHits(essay)
        words = len(essay.split())
        v = {}
        v['argumentPhraseCount']   = hits
        v['argumentPhrasePct'  ]   = float(hits) / words 
        return v

def essaySpaceCounts(essay):
    # returns a list of the number of spaces between the essay's words 
    s = [c for c in essay]
    SPACE = ' '
    space_counts = []
    while s:
        space_count = 0
        while s and s[0]==SPACE:
            s.pop(0)
            space_count += 1
        if space_count:
            space_counts.append(space_count)
        while s and s[0]!=SPACE:
            s.pop(0)
    return space_counts

def spacesStats(essay, **kwargs):
    # these stats *may* indicate paragraph breaks for some essay sets
    sc = numpy.array( essaySpaceCounts(essay) )
    v = {}
    v['spacesGrEq2Count'] =       len(sc[sc>=2]) 
    v['spacesGrEq5Count'] =       len(sc[sc>=5]) 
    v['spacesGrEq2Pct'  ] = float(len(sc[sc>=2])) / max(len(sc),1) # prevent /0 if no-space 1 word essay
    v['spacesGrEq5Pct'  ] = float(len(sc[sc>=5])) / max(len(sc),1)
    return v


def itemsEntropy(items):
    counts = uniqCounts(items)
    num_items = len(items)
    entropy = 0.0
    for item in counts:
        prob = counts[item] / float(num_items)
        entropy += prob * math.log(prob)
    return entropy

def entropyStats(essay, **kwargs):
    words = essay.split()
    v = {}
    v['entropyWords']       = itemsEntropy( words )
    v['entropyWordsLen']    = itemsEntropy([len(w) for w in     words ])
    v['entropyUniqWordsLen']= itemsEntropy([len(w) for w in set(words)])
    return v

class SyllablesEngine:

    def __init__(self):
        self.syls = nltk.corpus.cmudict.dict() # persistant dictionary of word syllables

    def nsyl(self, word):
        if word.lower() in self.syls:
            return [len(list(y for y in x if y[-1].isdigit())) for x in self.syls[word.lower()]]
        else:
            return [0]

    def essay_nsyl(self, essay):
        tot_syl = 0 
        for word in essay.split():
            tot_syl += min(self.nsyl(word))
        return tot_syl

    def syllablesStats(self, essay, **kwargs):
        essay_stop = rmStopWords(essay)
        v = {}
        v['nSyllablesAllWords']       = self.essay_nsyl( essay  )
        v['nSyllablesAllWordsNoStop'] = self.essay_nsyl( essay_stop  )
        uniq_essay      = ' '.join(set(essay.split()))
        uniq_essay_stop = ' '.join(set(essay_stop.split()))
        v['nSyllablesUniqWords']        = self.essay_nsyl( uniq_essay )
        v['nSyllablesUniqWordsNoStop']  = self.essay_nsyl( uniq_essay_stop )
        return v


class WordStemmer:  # stemming is used to count words using common suffixes 

    def __init__(self):
        self.stemmer   = nltk.PorterStemmer()

    def countWordStems(self, text, **kwargs):
        tokens = nltk.word_tokenize(text)
        count = sum([1 for t in tokens if t.lower() != self.stemmer.stem(t).lower()])
        v = {}
        v['nWordStems'] = count 
        return v

        
# ---------- end of feature creation functions 

def writeFeatures(statFunctions, fin_name, fout_name): 

    print "Generating features"
    print "Reading from:", fin_name
    print "Writing to  :", fout_name 
    fin = open(fin_name,  "r")
    fout= open(fout_name, "w")

    header_done = False
    header = fin.readline().split('\t')
    for line in fin:
        fields = line.split('\t')
        essay_id, essay_set, essay = fields[0], fields[1], fields[2]
        stats = {}
        for statFunction in statFunctions:
            new_stats = statFunction(essay, essay_set=essay_set, essay_id=essay_id)
            """
            try:
                new_stats = statFunction(essay, essay_set=essay_set, essay_id=essay_id)
            except:
                print "ERROR processing essay_id:", essay_id, "using statFunction:", statFunction
                raise SystemExit
            """
            stats = dict( stats.items() + new_stats.items() )

        outString = ','.join( [essay_id, essay_set ] + \
                              [str(stats[stat]) for stat in sorted(stats)] ) 

        if not header_done: 
            outHeader = "essay_id,essay_set,"
            outHeader += ','.join(["CH_"+stat for stat in sorted(stats)]) # also adds my initials
            fout.write(outHeader+'\n')
            header_done = True
            print "Features being geneated:"
            for n, ftr in enumerate(outHeader.split(',')):
                print n,ftr
            print "\nProcessing essay_id:", 
            sys.stdout.flush()
        
        fout.write(outString+'\n')

        if int(essay_id) % PRINT_STATUS_MOD == 0:
            print essay_id, 
            sys.stdout.flush()

    fout.close()
    fin.close()
    print "\nDone. Wrote features to:", fout_name


# ======   main   =========

if len(sys.argv) != 3:
    print "usage: python xfeatures.py <infile> <outfile>"
else:
    FIN  = sys.argv[1]
    FOUT = sys.argv[2]

    smav = SubjModalAuxVerbs( phrase_list=['would', 'could', 'should', 'might', 'may'] )
    arg  = ArgumentPhrases( phrase_file=ARGUMENT_PHRASES )
    prst = PromptStats()
    syll = SyllablesEngine()
    wstm = WordStemmer()

    statFunctions = [   styleStats, \
                        miscStyleStats, \
                        spellingStats,  \
                        anonStats, \
                        miscStats, \
                        gzipStats, \
                        randStats, \
                        vocabStats, \
                        arg.argPhraseStats, \
                        smav.subjModalAuxVerbStats, \
                        spacesStats, \
                        prst.promptStats, \
                        entropyStats, \
                        syll.syllablesStats,  \
                        wstm.countWordStems \
                    ]

    writeFeatures(statFunctions, FIN, FOUT)



