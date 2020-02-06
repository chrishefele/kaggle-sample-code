"""
# SyntacticComplexityEngine
#
# Computes various measures of syntatic complexity based on metrics given in this paper: 
#     Lu, Xiaofei (2010). Automatic analysis of syntactic complexity in second language writing.,
#     International Journal of Corpus Linguistics, 15(4):474-496.
#
# Basically, we search the parse trees for matching patterns using tregex, and 
# compute the metrics/features from the counts of those matches 
"""

DEBUG = False     # turns on / off debug printing 

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

SKIP_LIST = ['S']   # metrics to NOT return, due to feature duplication with others
                    # 'S' is just the sentence counts


import sys, os, commands, re
from java.io   import StringReader
from java.lang import String
from edu.stanford.nlp import *
from edu.stanford.nlp.trees        import PennTreeReader, LabeledScoredTreeFactory
from edu.stanford.nlp.trees.tregex import TregexPattern, TregexMatcher 


class SyntacticComplexityEngine:

    def __init__(self): 
        pattern = {}
        # The following is a list of tregex patterns for various structures:
        # sentences (S)
        pattern['S']  = "ROOT" 
        # verb phrase (VP)
        pattern['VP'] = "VP > S|SQ|SINV" 
        # clause (C)
        pattern['C']  = "S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < (VP <# (MD|VBP|VBZ|VBD))])" 
        # T-unit (T)
        pattern['T']  = "S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]" 
        # dependent clause (DC)
        pattern['DC'] = "SBAR < (S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < (VP <# (MD|VBP|VBZ|VBD))]))" 
        # complex T-unit (CT)
        pattern['CT'] = "S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << " + \
                         "(SBAR < (S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < (VP <# (MD|VBP|VBZ|VBD))])))"
        # coordinate phrase (CP)
        pattern['CP'] = "ADJP|ADVP|NP|VP < CC" 
        # complex nominal (CN)
        pattern['CN1']= "NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]"
        pattern['CN2']= "SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]"
        pattern['CN3']= "S < (VP <# VBG|TO) $+ VP"
        # fragment clause
        pattern['FC'] ="FRAG > ROOT !<< (S|SINV|SQ < (VP <# MD|VBP|VBZ|VBD))" 
        # fragment T-unit
        pattern['FT'] ="FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])"
        # list of patterns to search for
        self.pattern_regex = pattern

    def division(self, x, y):
        # utility function, used below, to divide numbers from strings & avoid /0 
        if float(x)==0 or float(y)==0:
            return 0
        return float(x)/float(y)

    def parseTextToParseTreeObj(self, parsed_essay):
        # converts from parse text to a Java Tree object needed by the Stnaformd Parser & Tregex
        parse_trees_text = '('+parsed_essay+ ')'
        tree_reader = PennTreeReader( StringReader(parse_trees_text), LabeledScoredTreeFactory() )
        new_tree_obj = tree_reader.readTree() 
        # print "Reconstructed parse:\n", new_tree_obj.toString()
        return new_tree_obj


    def syntacticComplexityStats(self, parsed_essay):
        v = {} # dictionary container for returned values

        # query the parse trees using tregex to count all matching patterns
        parse_tree_obj = self.parseTextToParseTreeObj(parsed_essay)
        for pattern_name in self.pattern_regex:
            # get count of pattern in parse_tree_obj
            if DEBUG: 
                print "\nPattern name :", pattern_name
                print "Pattern regex:", self.pattern_regex[pattern_name]
            pattern_regex = self.pattern_regex[pattern_name]
            compiled_pattern = TregexPattern.compile(pattern_regex)
            tree_matches = compiled_pattern.matcher(parse_tree_obj)
            n_matches = 0 
            while tree_matches.find():
                if DEBUG: 
                    print "Next pattern match in tree:"
                    tree_matches.getMatch().pennPrint()
                match_string = tree_matches.getMatch().toString()
                n_matches += 1
            if DEBUG: print n_matches, "matches found"
            v[pattern_name] = n_matches 

        # update frequencies of complex nominals, clauses, and T-units
        v['CN1'] += v['CN2'] + v['CN3']
        v['CN' ]  = v['CN1'] 
        v['C'  ] += v['FC' ] 
        v['T'  ] += v['FT' ]

        # compute the 14 syntactic complexity ratios 
        w = len(re.findall("\([A-Z]+\$? [^\)\(]+\)", parsed_essay)) # word count
        s,vp,c,t,dc,ct,cp,cn = [ v[ix] for ix in ('S','VP','C','T','DC','CT','CP','CN') ]
        v['MLS'   ] = self.division(w,  s)
        v['MLT'   ] = self.division(w,  t)
        v['MLC'   ] = self.division(w,  c)
        v['CperS' ] = self.division(c,  s)
        v['VPperT'] = self.division(vp, t)
        v['CperT' ] = self.division(c,  t)
        v['DCperC'] = self.division(dc, c)
        v['DCperT'] = self.division(dc, t)
        v['TperS' ] = self.division(t,  s)
        v['CTperT'] = self.division(ct, t)
        v['CPperT'] = self.division(cp, t)
        v['CPperC'] = self.division(cp, c)
        v['CNperT'] = self.division(cn, t)
        v['CNperC'] = self.division(cn, c)

        # rename/prefix the metrics (by copying them)
        v_syntactic = {}
        for key in v:
            if key not in SKIP_LIST:
                v_syntactic['parseSyntax'+key] = v[key]
        return v_syntactic

    """
    The code above counts the occurrences of the following 9 structures in the text: 

    words (W), 
    sentences (S), 
    verb phrases (VP), 
    clauses (C), 
    T-units (T), 
    dependent clauses (DC), 
    complex T-units (CT), 
    coordinate phrases (CP), 
    complex nominals (CN).  

    These frequency counts are then used to compute the 
    following 14 syntactic complexity indices of the text: 

    mean length of sentence (MLS), 
    mean length of T-unit (MLT), 
    mean length of clause (MLC), 
    clauses per sentence (CperS), 
    verb phrases per T-unit (VPperT), 
    clauses per T-unit (CperT), 
    dependent clauses per clause (DCperC), dependent 
    clauses per T-unit (DCperT), 
    T-units per sentence (TperS), 
    complex T-unit ratio (CTperT), 
    coordinate phrases per T-unit (CPperT), 
    coordinate phrases per clause (CPperC), 
    complex nominals per T-unit (CNperT), 
    complex nominals per clause (CNperC). 

    """

def testSyntacticComplexityEngine():
    print "\n*** SyntacticComplexityEngine() TEST code ***"
    sce = SyntacticComplexityEngine()
    example_parsed_essay = "(ROOT (S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test))) (. .))) (ROOT (S (NP (PRP She)) (VP (VBZ sells) (NP (NN sea) (NNS shells)) (PRT (RP down)) (PP (IN by) (NP (DT the) (NN seashore)))) (. .))) (ROOT (S (NP (NP (DT The) (NN rain)) (PP (IN in) (NP (NNP Spain)))) (VP (VBZ falls) (ADVP (RB mainly)) (PP (IN on) (NP (DT the) (NN plain)))) (. .))) (ROOT (S (NP (NNP Mary)) (VP (VBD had) (NP (DT a) (JJ little) (NN lamb))) (. .))) (ROOT (S (NP (PRP$ Its) (NN fleece)) (VP (VBD was) (ADJP (JJ white) (PP (IN as) (NP (NN snow))))) (. .)))"
    print "Example parsed essay:"
    print example_parsed_essay
    print "calculating stats of example essay"
    stats = sce.syntacticComplexityStats(example_parsed_essay)
    print "returned dictionary of stats:"
    print stats

if __name__ == "__main__":
    testSyntacticComplexityEngine()


