from NGramIndex import NGramIndex
import nltk
import random
import Levenshtein as lev

def median_word(words, word_counts):
    median = lev.median(words, word_counts)
    while True:
        last_median = median
        median = lev.median_improve(median, words, word_counts)
        if median == last_median:
            break
    return median

trigrams = NGramIndex('../data/3_grams.txt', 1, min_count=20)

holdout = open('../data/holdout.txt','r')
for line_num, line in enumerate(holdout):
    words = line.rstrip().split()
    if len(words) < 3 or len(words) > 15:  # to fit on screen during testing 
        continue
    del_word_posn = random.randint(1, len(words)-2)
    del_word = words[del_word_posn]
    words = words[0:del_word_posn] + words[(del_word_posn+1):]

    print
    for word_num, word in enumerate(line.rstrip().split()):
        print word if word_num != del_word_posn else "<<"+del_word+">>" , 
    print 

    for ix in range(len(words)-1):
        word_left  = words[ix  ]
        word_right = words[ix+1]
        context_words = [word_left, word_right]
        candidates = [(count, word) for word, count in trigrams.insert_word_suggestions(context_words)]
        if len(candidates) > 0:
            best_word = max(candidates)[1] 
        else:
            best_word = ""
        print ' '.join(words[0:(ix+1)]), 
        print ' <' + best_word + '> ', 
        print ' '.join(words[(ix+1):])

        med_words  = [word  for count, word in candidates] + ['ae',]
        med_counts = [count for count, word in candidates] + [1,]
        mw = median_word(med_words, med_counts)
        print "%8i CANDIDATES, MEDIAN_WORD = %s" % (len(candidates), mw)

        #for count, candidate in sorted(candidates):
        #    print "\t", candidate, count
        #print '----------------' 

