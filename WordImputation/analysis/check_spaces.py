
# script to verify spacing between train tokens are always 1 space

fin = open('../download/train_v2.txt','r')

for n, line in enumerate(fin):
    #line = line.rstrip() # strip off terminating \n
    line = line[:-1]
    line_ss = ' '.join(line.split())  # single spaces between tokens 
    if line_ss != line:
        print "*****", n, line.split()
    if n % 1000000 == 0:
        print n
fin.close()

