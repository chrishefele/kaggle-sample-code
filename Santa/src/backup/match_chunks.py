import pandas
import sys

FNAME   = sys.argv[1]   # '../backbone/nnpath_backbone.csv'
NCHUNKS = int(sys.argv[2])   # 10000

def chunks(l, n):
    # split a list into chunks of length n
    return [l[i:i+n] for i in range(0, len(l), n)]

df = pandas.read_csv(FNAME)
tour1 = df['path1']
tour2 = df['path2']

print 
print "checking",FNAME,"with chunks of length:",NCHUNKS
print
chunk_mismatch = False
for n, (chunk1, chunk2) in enumerate(zip(chunks(tour1,NCHUNKS), chunks(tour2,NCHUNKS))):
    n_union        = len(set(chunk1).union(       set(chunk2)))
    n_intersection = len(set(chunk1).intersection(set(chunk2)))
    print "chunk:",n,"node_union:", n_union, "node_intersection:", n_intersection
    if n_union != n_intersection:
        chunk_mismatch=True

print 
if chunk_mismatch:
    print "*** ERROR ***  CHUNK_MISMATCH detected"
else:
    print "No errors detected"
print
