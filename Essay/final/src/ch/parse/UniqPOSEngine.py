from reTag import reTag

class UniqPOSEngine:
    def __init__(self):
        # Penn Treebank Part-of-Speech (POS) tags of interest
        poss =  "CC CD DT EX FW IN JJ JJR JJS LS MD NN NNP NNPS NNS PDT POS PRP PRP$ " + \
                "RB RBR RBS RP SYM TO UH VB VBD VBG VBN VBP VBZ WDT WP WP$ WRB X"
        self.target_pos_tags = [reTag(tag) for tag in poss.split()] 

    def numUniqPOS(self, parse):
        # get parse tree leaf pairs  e.g. (POS word)
        tokens = parse.split()
        pad = ['']
        token_pairs = zip(pad+tokens, tokens+pad)
        pos_word_pairs = [(t0,t1) for t0, t1 in token_pairs if '(' in t0 and ')' in t1]
        #print pos_word_pairs

        # count number of unique words, broken down by POS
        pos_count = {}
        for pos, word in pos_word_pairs:
            pos  = reTag(pos.replace( '(',''))
            word = word.replace(')','')
            pos_count.setdefault(pos,{})
            pos_count[pos].setdefault(word,0) 
            pos_count[pos][word] += 1

        v = {}
        for pos in self.target_pos_tags:
            pos_count.setdefault(pos,{})
            v['parseNumUniq'+pos] = len(pos_count[pos])
        assert len(v) == len(self.target_pos_tags)  # paranoia...ensures const num of columns
        return v


if __name__=='__main__':

    example_parsed_essay = "(ROOT (S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test))) (. .))) (ROOT (S (NP (PRP She)) (VP (VBZ sells) (NP (NN sea) (NNS shells)) (PRT (RP down)) (PP (IN by) (NP (DT the) (NN seashore)))) (. .))) (ROOT (S (NP (NP (DT The) (NN rain)) (PP (IN in) (NP (NNP Spain)))) (VP (VBZ falls) (ADVP (RB mainly)) (PP (IN on) (NP (DT the) (NN plain)))) (. .))) (ROOT (S (NP (NNP Mary)) (VP (VBD had) (NP (DT a) (JJ little) (NN lamb))) (. .))) (ROOT (S (NP (PRP$ Its) (NN fleece)) (VP (VBD was) (ADJP (JJ white) (PP (IN as) (NP (NN snow))))) (. .)))"
    print example_parsed_essay 
    print

    upe = UniqPOSEngine()
    print sorted(upe.numUniqPOS(example_parsed_essay).items())
    print
    repeated_essay = 100*(example_parsed_essay+' ')
    print sorted(upe.numUniqPOS(repeated_essay      ).items())


