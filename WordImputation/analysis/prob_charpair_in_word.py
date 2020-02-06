
# prints prob that each char pair appears in a randomly selected word

from collections import defaultdict

MAX_LINES = pow(2,30) # 45sec/million

word_count = 0 
char_counts = defaultdict(int)
fin = open('../download/train_v2.txt','r')
for line_num, line in enumerate(fin):
    if line_num > MAX_LINES:
        break
    for word in line.rstrip().split():
        word_count += 1 

        # create all letter pairs in word, where first preceeds second
        pairs = set()
        for let1_ix in xrange(0,len(word)-1):
            for let2_ix in xrange(let1_ix+1,len(word)):
                char_pair = word[let1_ix] + word[let2_ix]
                pairs.add(char_pair)
        for char_pair in pairs:
            char_counts[char_pair] += 1

fin.close()
print "lines:", line_num, "words:", word_count

results = [(float(count)/word_count, char) for char, count in char_counts.items()]

for prob, char in sorted(results, reverse=True):
    print prob, char

