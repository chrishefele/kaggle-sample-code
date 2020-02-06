# DependencyDistanceEngine
#
# This code calculates the syntactic dependency distance as dscribed in:
# "Syntactic Dependency Distance as a Sentence Complexity Measure" by Masanori Oya
# 
# Basically, it measures the average distance (in words) between words that are 
# dependent on each other (e.g. subject-object), based on the parser output. 
# e.g. 
#   "Sentences  are  easier to read when constructed this way."
#   "Sentences, when constructed this way, are harder to read."
#
# by CJH 2/26/2012
#

DEBUG = False   # turns on / off debug printing 

import sys
#PARSER_DIR        = "/home/chefele/Essay/parse/stanford-parser-2012-02-03/" 
PARSER_DIR        = "./stanford-parser-2012-02-03/" 
PARSER_JAR        = PARSER_DIR + "stanford-parser.jar"
PARSER_GRAMMAR    = PARSER_DIR + "grammar/englishPCFG.ser.gz"
sys.path.append(PARSER_JAR)
#TREGEX_DIR        = "/home/chefele/Essay/parse/stanford-tregex-2012-01-06/"
TREGEX_DIR        = "./stanford-tregex-2012-01-06/"
TREGEX_JAR        = TREGEX_DIR + "stanford-tregex.jar"
sys.path.append(TREGEX_JAR)

import sys, os, commands, re
from java.io   import StringReader
from java.lang import String
from edu.stanford.nlp import *
from edu.stanford.nlp.trees        import PennTreeReader, LabeledScoredTreeFactory
from edu.stanford.nlp.trees        import PennTreebankLanguagePack
from edu.stanford.nlp.trees.tregex import TregexPattern, TregexMatcher 


class DependencyDistanceEngine:

    def __init__(self):
        tlp      = PennTreebankLanguagePack()
        self.gsf = tlp.grammaticalStructureFactory()

    def calcDistsAvg(self, dists_sum, dists_num):
        if dists_num > 0:
            return float(dists_sum) / dists_num
        else:
            return 0 

    def sentenceDependencyDistance(self, sentence_tree):
        # TODO remove 2 lines below, since moved to constructor for speed? 
        # tlp = PennTreebankLanguagePack()
        # gsf = tlp.grammaticalStructureFactory()
        gs  = self.gsf.newGrammaticalStructure(sentence_tree)
        tdl = gs.typedDependenciesCCprocessed() # list of typed word dependencies 
        if DEBUG: 
            print "\nTyped Dependencies:"
        # looop through list of typed word dependencies between word pairs 
        dists_num = 0
        dists_sum = 0
        for td in tdl:
            w1_ix = td.gov().index()  # word positions in sentence
            w2_ix = td.dep().index()
            dist = abs(w1_ix - w2_ix) # word distance between dependent words 
            ROOT_IX = 0 # root node 'pseudo-position'
            touches_root_node = (w1_ix==ROOT_IX or w2_ix==ROOT_IX)
            if not touches_root_node:  # skip links to root (root is no real position) 
                dists_sum += dist
                dists_num += 1
            elif DEBUG:
                print "*** Skipping root node below"
            if DEBUG:
                print td.toString(), dist
        dists_avg = self.calcDistsAvg(dists_sum, dists_num)
        return dists_avg

    def dependencyDistanceStats(self, parsed_essay):
        # converts from parse text to a Java Tree object needed by the Stnaformd Parser 
        trees_text = '('+parsed_essay+')'
        trees_reader = PennTreeReader( StringReader(trees_text), LabeledScoredTreeFactory() )
        tree = trees_reader.readTree()
        if DEBUG: 
            print "Reconstructed parse:\n", tree.toString(),"\n"

        # process sentences seperately; find sentences by matching "ROOT" nodes in the parse tree
        sentence_pattern = TregexPattern.compile("ROOT")
        tree_sentences = sentence_pattern.matcher(tree)

        dists_sum = 0
        dists_num = 0
        while tree_sentences.find():  # for each sentence...
            tree_sentence = tree_sentences.getMatch()
            if DEBUG: 
                print "Next sentence found in tree:"
                print tree_sentence.toString()
            sdd = self.sentenceDependencyDistance(tree_sentence)
            dists_sum += sdd
            dists_num += 1
            if DEBUG: 
                print "Sentence dependency distance:", sdd, "\n"

        dists_avg = self.calcDistsAvg(dists_sum, dists_num)
        if DEBUG:
            print "<<Essay>> dependency distance:", dists_avg, "\n"
        v = { 'dependencyDistance': dists_avg}
        return v


def testDependencyDistanceEngine():
    print "\n*** DependencyDistanceEngine() TEST code ***"
    dde = DependencyDistanceEngine()
    example_parsed_essay = "(ROOT (S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test))) (. .))) (ROOT (S (NP (PRP She)) (VP (VBZ sells) (NP (NN sea) (NNS shells)) (PRT (RP down)) (PP (IN by) (NP (DT the) (NN seashore)))) (. .))) (ROOT (S (NP (NP (DT The) (NN rain)) (PP (IN in) (NP (NNP Spain)))) (VP (VBZ falls) (ADVP (RB mainly)) (PP (IN on) (NP (DT the) (NN plain)))) (. .))) (ROOT (S (NP (NNP Mary)) (VP (VBD had) (NP (DT a) (JJ little) (NN lamb))) (. .))) (ROOT (S (NP (PRP$ Its) (NN fleece)) (VP (VBD was) (ADJP (JJ white) (PP (IN as) (NP (NN snow))))) (. .)))"
    print "Example parsed essay:"
    print example_parsed_essay
    print "calculating stats of example essay"
    stats = dde.dependencyDistanceStats(example_parsed_essay)
    print "returned dictionary of stats:"
    print stats

if __name__ == "__main__":
    testDependencyDistanceEngine()


