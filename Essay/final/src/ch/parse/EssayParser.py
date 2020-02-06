# EssayParser.py 
# 2/5/2012 by Chris Hefele
#
# This module contains just one class which uses the 
# Stanford Statistical Parser to parse the essays.
# The parse can be used to create grammar-based features.
#
# Note: this code requires the following installed:
# 1. Jython  
# 2. The Stanford Statistical Parser version 2.0  (written in Java)
#   (http://nlp.stanford.edu/software/lex-parser.shtml)
#

#PARSER_DIR        = "/home/chefele/Essay/parse/stanford-parser-2012-02-03/" 
PARSER_DIR        = "./stanford-parser-2012-02-03/" 
PARSER_JAR        = PARSER_DIR + "stanford-parser.jar"
PARSER_GRAMMAR    = PARSER_DIR + "grammar/englishPCFG.ser.gz"

import sys
sys.path.append(PARSER_JAR)
from java.io   import CharArrayReader
from java.io   import StringReader
from java.lang import String
from jarray    import array
from edu.stanford.nlp import *
from edu.stanford.nlp.trees import PennTreeReader, LabeledScoredTreeFactory


class EssayParser:
    def __init__(self):
        # initialize the parser & make it persistent (initialization takes a few seconds)
        parser_option_flags = array(["-maxLength", "100", "-retainTmpSubcategories"], String)
        self.lxparser  = parser.lexparser.LexicalizedParser(PARSER_GRAMMAR, parser_option_flags)

    def parse(self, essay):
        parsed_essay = ""
        parsed_essay_objs = []
        for sentence in process.DocumentPreprocessor(StringReader(essay)):
            parse = self.lxparser.apply(sentence)
            parsed_essay += " " + parse.toString()
            parsed_essay_objs.append(parse)
            # print "."
        return (parsed_essay, parsed_essay_objs)

def testEssayParser():
    print "\n*** EssayParser() running TEST code ***"
    essay  = " This is a test.  She sells sea shells down by the seashore."
    essay += " The rain in Spain falls mainly on the plain." 
    essay += " Mary had a little lamb.  Its fleece was white as snow."
    print "TEST essay to parse:\n", essay 
    ep = EssayParser()
    ep_parse, ep_parse_tree_objs = ep.parse(essay)
    print "\nParsed essay:\n", ep_parse

    # now test going from a parse tree text representation back to a tree object
    print "\nNow converting: parse_text -> tree_object"
    parse_trees_text = '(' + ep_parse + ')'
    tree_reader = PennTreeReader( StringReader(parse_trees_text), LabeledScoredTreeFactory() )
    new_tree = tree_reader.readTree() # new_tree is a java object 
    print "Reconstructed parse:\n", new_tree.toString()


if __name__ == "__main__":
    testEssayParser()

