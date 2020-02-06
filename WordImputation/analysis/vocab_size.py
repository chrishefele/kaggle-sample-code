import sys

print "reading unigrams"
fin = open("n1gram.txt")
word_rank = {}
for n, line in enumerate(fin):
    tokens = line.split()
    count = int(tokens[0])
    word  = tokens[1]
    rank = n + 1
    word_rank[word] = rank 
fin.close()
print "done reading unigrams"

fin  = open("n3gram.txt")
fout = open("vocab_size.csv", "w")
fout.write("count,maxrank\n") # trigram count and max of the 3 individual word unigram ranks
unknown_line = 0
for n, line in enumerate(fin):
    tokens = line.split()
    count = int(tokens[0])
    words  = tokens[1:]
    word_ranks = [word_rank.get(word, 0) for word in words]
    if max(word_ranks) > 0:
        #print count, words, word_ranks, max(word_ranks)
        fout.write( str(count) + "," + str(max(word_ranks)) + "\n" )
    else:
        unknown_line += 1
    if n % 1000000 == 0:
        print n , 
        sys.stdout.flush()
fin.close()
fout.close()
print "Done"
print "lines read   :", n
print "unknown lines:", unknown_line
print "% unknown    :", 100.0 * unknown_line / n ,"%"




