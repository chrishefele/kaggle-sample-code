
# prints avg number of times a char appears in a randomly selected word

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
        for char in list(word): # NOTE: list(), not set(), so duplicates included
            char_counts[char] += 1
fin.close()
print "lines:", line_num, "words:", word_count

results = [(float(count)/word_count, char) for char, count in char_counts.items()]

for prob, char in sorted(results, reverse=True):
    print prob, char

