import sys

INVERT_FLAG = False
INVERT_THRESHOLD = 500000 # if more than this, use nonzero(1+(data+zeros)) vs the data

TRAIN = "/home/chefele/SemiSupervised/download/competition_data/unlabeled_data.svmlight.dat"
TRAIN_LINES = 1000000

line_counter = 0
col_vals = {}

print "Reading:", TRAIN
print "Reading line:",

for line in open(TRAIN,"r"):
    line_counter+=1
    if line_counter % 10000 ==0:
        print line_counter,
        sys.stdout.flush()
    for field in line.split(" "):
        if ":" in field:
            tokens = field.split(":")

            col = int(tokens[0])
            col_val = float(tokens[1])

            if col not in col_vals:
                col_vals[col]=[]
            col_vals[col].append(col_val)  


def invert_data(data):
    num_zeros = TRAIN_LINES - len(data)
    data_plus_zeros = data + [0]*num_zeros
    data_inverted = [1-dz for dz in data_plus_zeros if (1-dz)!=0]
    return( data_inverted )

print "Checking for columns requiring inverted values..." 
for col in col_vals:
    if INVERT_FLAG and (len(col_vals[col]) > INVERT_THRESHOLD) :
        old_len = len(col_vals[col])
        col_vals[col] = invert_data( col_vals[col] ) 
        if col_vals[col]==[]:
            col_vals[col]=[0]
        new_len = len(col_vals[col])
        print "Inverted Col:", col,"Length before:", old_len, "After inverted:", new_len
        sys.stdout.flush()


# count_stats = sorted([(vals[val], val) for val in vals])
# print count_stats

tot_cnt = 0 
print "Sorting..."
sys.stdout.flush()
col_count_stats = sorted([(len(col_vals[col]), col) for col in col_vals])
for n, (cnt, col) in enumerate(col_count_stats):
    tot_cnt += cnt
    print n, 
    print "Col:", col, "NumVals:", len(col_vals[col]),
    uniques=len(set(col_vals[col]))
    print "Uniques:", uniques,
    print "CumPts:", tot_cnt, 
    print "Max:", max(col_vals[col]), "Min:",min(col_vals[col]),
    print "Avg:", sum(col_vals[col])*1.0/len(col_vals[col]),
    sys.stdout.flush()
    
    # only write non-binary column values (or potentiall thresholded to 0/1)
    # (seems ok if min values ==1, then <1-->0  & >=1-->1 ) 
    if uniques>1 : 
        print "Writing...",
        fout=open("col_vals_"+str(col)+".csv","w")
        for aVal in col_vals[col]:
            fout.write(str(aVal)+"\n")
        fout.close()

    print

