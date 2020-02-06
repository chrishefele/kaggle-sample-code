fin = open('../download/train.txt','r')
for n, line in enumerate(fin):
    if n % 1000000 == 0:
        print n
fin.close()

