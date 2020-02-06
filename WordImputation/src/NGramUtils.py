import nltk

def positionNGram(words, word_posn, ngram_length, ngram_insert_posn):
    # extract an ngram from a sentence given some parameters
    ix_left, ix_right, ngram_within_sentence = \
        ngram_indexes(words, word_posn, ngram_length, ngram_insert_posn)
    if ngram_within_sentence:
        return tuple(words[ix_left:(ix_right+1)])
    else:
        return None 

def positionNGramInverse(words, word_posn, ngram_length, ngram_insert_posn):
    # returns all words in a sentence except for words in the specified ngram 
    ix_left, ix_right, ngram_within_sentence = \
        ngram_indexes(words, word_posn, ngram_length, ngram_insert_posn)
    if ngram_within_sentence:
        return tuple(words[:ix_left] + words[(ix_right+1):] ) 
    else:
        return None 

def ngram_indexes(words, word_posn, ngram_length, ngram_insert_posn):
    assert ngram_length >= 2
    assert 0 <= word_posn < len(words) -1 
    assert 0 <= ngram_insert_posn < ngram_length - 1 

    # Calculate sentence positions of the first & last words in the proposed ngram.
    # ngram_insert_posn is the point after which to insert a (possibly) missing word.
    # This is aligned to the word_posn, and nleft/nright words are taken from either side.
    # This forms the proposed ngram (provided all words are within sentence boundries).

    nwords   = len(words)
    nleft    = ngram_insert_posn
    nright   = ngram_length - ngram_insert_posn -1 
    ix_left  = word_posn - nleft
    ix_right = word_posn + nright
    ngram_within_sentence = (0 <= ix_left < nwords) and (0 <= ix_right < nwords)
    return ix_left, ix_right, ngram_within_sentence


def positionNGrams(words, ngram_length, ngram_insert_posn):
    return [positionNGram(       words, posn, ngram_len, ngram_insert_posn) for posn in range(len(words)-1)]

def positionNGramsInverse(words, ngram_length, ngram_insert_posn):
    return [positionNGramInverse(words, posn, ngram_len, ngram_insert_posn) for posn in range(len(words)-1)]

def ngrams(words, ngram_length, insert_posn):
    assert ngram_length >= 2
    # insert posn (by my convention) is between the N-th and N+1-th word
    assert 0 <= insert_posn < ngram_length - 1 

    # For consistency with other code that assumed bigrams only, 
    # I want to create the same number of N_grams per sentence 
    # as bigrams per sentence.  To do that, I add 'None' padding 
    # below for N-grams longer than 2. Generally,  reating N_grams 
    # from a W word sentence yields W-(N-1) N_grams.
    ngrams = nltk.util.ngrams(words, ngram_length)
    if len(words) >= ngram_length: 
        npad       = ngram_length - 2
        npad_left  =        insert_posn 
        npad_right = npad - npad_left 
        return npad_left*[None] + ngrams + npad_right*[None]
    else:
        return (len(words)-1) * [None]


if __name__ == '__main__':
    for sentence_length in range(6+1):
        words = [c for n, c in enumerate('ABCDEF') if n < sentence_length]
        print "\nSentence:", words
        for ngram_len in [2,3,4,5]:
            for insert_position in range(0, ngram_len-1): 
                print "ngram_len:", ngram_len, "insert_posn:", insert_position
                ng1 = ngrams(        words, ngram_len, insert_position)
                ng2 = positionNGrams(words, ngram_len, insert_position)
                print ng1
                print ng2 
                print "Equal?:", tuple(ng1) == tuple(ng2)
                #
                ng2i= positionNGramsInverse(words, ngram_len, insert_position)
                print "ngram        :", ng2 
                print "ngram-inverse:", ng2i
                print 


