# usage:   python indegree_args.py <infile>  <outfile>

#TRAINING_FILE="/home/chefele/SocialNetwork/download/social_train.csv"
#TRAINING_FILE="/home/chefele/SocialNetwork/download/social_test.txt"

import sys
TRAINING_FILE = sys.argv[1]
RESULTS_FILE  = sys.argv[2]

MAX_VERTEX_ID = 1133547

vout_vin={}
vin_vout={}
vall={}
print "Initializing"
for ix in xrange(1,MAX_VERTEX_ID+1):
    vout_vin[ix]=[]
    vin_vout[ix]=[]
    vall[ix]=[]

print "Opening:",TRAINING_FILE
fin=open(TRAINING_FILE)
linecounter=0
print "Reading line:",
for line in fin.readlines():
    linecounter+=1
    if linecounter % 100000 == 0:
        print linecounter,
        sys.stdout.flush()
    tokens=line.split(",")
    vout,vin=(int(tokens[0]),int(tokens[1]))
    vall[vin].append(vout)
    vall[vout].append(vin)
    vin_vout[vin].append(vout)
    vout_vin[vout].append(vin)
print "Done reading"

# count indegrees
indegree_counts={}
for vin in vin_vout:
    indegree=len(vin_vout[vin])
    if not(indegree in indegree_counts):
        indegree_counts[indegree]=0
    indegree_counts[indegree]+=1
print "done" 

report=[]
for indegree_count in indegree_counts:
    report.append((indegree_count,indegree_counts[indegree_count]))
report.sort()

print "writing results to :",RESULTS_FILE
fout=open(RESULTS_FILE,"w")
for indegree, freq in report:
    fout.write(str(indegree)+","+str(freq)+"\n")
fout.close()

