# parseFeatures.py
# 2/8/2012 by Chris Hefele
#
# usage: jython parseFeatures.py <infile> <outfile> 
#
# This program takes each parsed essay in the input file & 
# creates a number of features # based on grammar, sentence structure, 
# parse-tree strutcure, etc. and writes it to outfile.
#

import sys
import copy
import math
from SyntacticComplexityEngine import SyntacticComplexityEngine
from DependencyDistanceEngine  import DependencyDistanceEngine 
from reTag import reTag
from UniqPOSEngine import UniqPOSEngine

def parseLine(line):
    fields = line.split('\t')
    #essay_id, essay_set, domain1_score, parse = fields[0], fields[1], fields[2], fields[3]
    essay_id, essay_set, parse = fields[0], fields[1], fields[2]
    return (essay_id, essay_set, parse)

def uniq(items): # use this instead of python 'set' since no sets in jython 2.2
    d = {}
    for item in items:
        d[item] = None
    return d.keys()


class ParseTagStatsEngine:

    def __init__(self, fin_name):
        # get all the tags ahead of time so one can recognize 0 counts of a tag in essays
        print "Pre-reading parse tags from :", fin_name
        sys.stdout.flush()
        self.emptyTagDict = {}
        for line in open(fin_name,  "r"):
            essay_id, essay_set, parse = parseLine(line)
            parseTags = [ reTag(token[1:]) for token in parse.split() if token[0]=='(' ]
            for parseTag in parseTags:
                self.emptyTagDict[parseTag] = 0
            if int(essay_id) % 1000 == 0:
                print essay_id, 
                sys.stdout.flush()
        print 
        print "Found", len(self.emptyTagDict),"parse tags"

    def parseTagStats(self, parse):
        # get the tags & count them 
        parseTags = [ reTag(token[1:]) for token in parse.split() if token[0]=='(' ]
        tagCounts = copy.deepcopy(self.emptyTagDict)
        for tag in parseTags:
            tagCounts[tag] += 1 

        nSentences = tagCounts["ROOT"]
        if tagCounts["ROOT"]==0 and tagCounts["X"]>0:
            nSentences = 1
        nTags = len(parseTags)

        v = {}
        # create features from ratios of each tag count 
        for tag in tagCounts:
            v['parse'+tag+'perSent'] = float(tagCounts[tag]) / nSentences
            v['parse'+tag+'count']   =       tagCounts[tag]
            v['parse'+tag+'pct']     = float(tagCounts[tag]) / nTags

        # overall tag counts & unique tag counts & related ratios
        v['parseNumTags'    ] =             len(     parseTags )
        v['parseNumUniqTags'] =             len(uniq(parseTags))
        v['parseNumUniqTagsPct' ] =   float(len(uniq(parseTags))) / len(parseTags)

        return v


class TreeStatsEngine:
    def cumsum(self, xlist):
        x_sum = 0
        x_cumulative = []
        for xi in xlist:
            x_sum += xi
            x_cumulative.append(x_sum)
        return x_cumulative

    def treeDepths(self, parse):  # depths at each tree node or leaf
        lookup = { '(':1, ')':-1 } 
        return self.cumsum([ lookup[c] for c in parse if c in '()' ]) 

    def leafDepths(self, parse):
        depths = self.treeDepths(parse)
        depths_nbrs = zip(depths[0:-3], depths[1:-2], depths[2:-1])
        leaf_depths = [ctr for lft, ctr, rt in depths_nbrs if ctr>lft and ctr>rt] # extract peaks
        return leaf_depths

    def numTreeLeaves(self, parse):
        parens = ''.join([c for c in parse if c in '()'])
        return parens.count('()')

    def numTreeBranches(self, parse):
        assert parse.count('(') == parse.count(')')
        return parse.count('(') - self.numTreeLeaves(parse)

    def treeStats(self, parse):
        leaves     = max(1,    self.numTreeLeaves(parse))
        branches   = max(1,    self.numTreeBranches(parse))
        depth_max  = max(1, max(self.leafDepths(parse)))
        leaf_depths = self.leafDepths(parse)
        depth_avg  = max(1,    float(sum(leaf_depths))/len(leaf_depths) ) 

        v = {}
        v["parseTreeLeaves"  ]      = leaves 
        v["parseTreeLogLeaves"]     = math.log(leaves)
        v["parseTreeBranches"]      = branches 
        v["parseTreeLeafDepthMax"]  = depth_max
        v["parseTreeLeafDepthAvg"]  = depth_avg 

        v["parseTreeBranchesDivLeaves"]        =    float(branches)     / float(leaves)
        v["parseTreeLeavesDivDepthAvg"]        =    float(leaves)       / float(depth_avg)   
        v["parseTreeBranchesDivDepthAvg"]      =    float(branches)     / float(depth_avg)   
        v["parseTreeLogLeavesDivDepthAvg"]     =    math.log(leaves)    / float(depth_avg)   
        v["parseTreeLogBranchesDivDepthAvg"]   =    math.log(branches)  / float(depth_avg)   
        return v


def sorted(adict): 
    # 'sorted' is standard in python 2.5+, etc. but not in jython 2.2, so need to recreate it 
    keys = adict.keys()
    keys.sort()
    return keys

def writeFeatures( statFunctions, fin_name, fout_name): 

    print "Reading from:", fin_name
    print "Writing to  :", fout_name 
    fin = open(fin_name,  "r")
    fout= open(fout_name, "w")

    header_done = False     # wrote header to output file yet? 
    # header = fin.readline().split('\t')
    for line in fin:
        essay_id, essay_set, parse = parseLine(line)
        stats = {}
        for statFunction in statFunctions:
            stats = dict( stats.items() + statFunction(parse).items() )

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
        fout.write(outString+'\n')
        # print ".",
        if int(essay_id) % 100 == 0:
            print essay_id, 
            sys.stdout.flush()
    fout.close()
    fin.close()
    print "\nDone. Wrote features to:", fout_name,"\n"

# ======   main   =========

print "\n*** Generating parse features ***"

if len(sys.argv) == 3:

    FIN  = sys.argv[1]
    FOUT = sys.argv[2]
    ptse = ParseTagStatsEngine(FIN)
    tse  = TreeStatsEngine()
    sce  = SyntacticComplexityEngine()
    upos = UniqPOSEngine()
    # dde  = DependencyDistanceEngine()  
    """
    # NOTE on function/method runtimes: 
    # dependencyDistanceStats takes 3 hours to run, and little gain
    # All the other functions take <5 minutes combined
    """
    statFunctions = [   ptse.parseTagStats, \
                        tse.treeStats, \
                        sce.syntacticComplexityStats, \
                        upos.numUniqPOS \
                    ] 
                        # dde.dependencyDistanceStats ] # removed this; little gains
    writeFeatures(statFunctions, FIN, FOUT)

else:
    print "usage: jython parseFeatures.py <infile> <outfile>"


