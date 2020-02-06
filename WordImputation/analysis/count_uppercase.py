
upper_count = lower_count = 0

for line in open("../data/train_ngrams_1+1.txt"):
    count, word = line.rstrip().split()
    count = int(count)
    if word.lower() == word:
        lower_count += count
    else:
        upper_count += count

print "count of ngrams unchanged by lowercasing:", lower_count
print "count of ngrams   changed by lowercasing:", upper_count

