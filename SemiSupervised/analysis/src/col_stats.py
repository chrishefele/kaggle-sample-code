import sys

TRAIN = "/home/chefele/SemiSupervised/download/competition_data/unlabeled_data.svmlight.dat"

line_counter = 0
col_vals = {}
col_counts = {}

print "Reading:", TRAIN
print "Reading line:",

for line in open(TRAIN,"r"):
    line_counter+=1
    if line_counter % 1000 ==0:
        print line_counter,
        sys.stdout.flush()
    for field in line.split(" "):
        if ":" in field:
            tokens = field.split(":")

            col = int(tokens[0])
            if col not in col_counts:
                col_counts[col] = 0
            col_counts[col] += 1

            col_val = float(tokens[1])
            if col not in col_vals:
                col_vals[col]=[]
            col_vals[col].append(col_val)  

# count_stats = sorted([(vals[val], val) for val in vals])
# print count_stats

tot_cnt = 0 
col_count_stats = sorted([(col_counts[col], col) for col in col_counts])
for n, (cnt, col) in enumerate(col_count_stats):
    tot_cnt += cnt
    print n, 
    print "Col:", col, "NumVals:", len(col_vals[col]),
    print "Uniques:", len(set(col_vals[col])),
    print "CumPts:", tot_cnt, 
    print "Max:", max(col_vals[col]), "Min:",min(col_vals[col]),
    print "Avg:", sum(col_vals[col])*1.0/len(col_vals[col])


