import sys

fin = open(sys.argv[1], 'r')
header = fin.readline().strip()
seen = set()
for n, line in enumerate(fin):
    if n % 1000 == 0: 
        print "reading line:", n
    fields     = line.split(',')
    record_ID  = int(fields[0])
    restofline = ','.join(fields[1:])
    if restofline in seen:
        print "DUPLICATE record:", record_ID
    seen.add(restofline)
