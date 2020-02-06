import sys
#TRAINING_FILE="/home/chefele/SocialNetwork/download/social_train.csv"
TRAINING_FILE="/home/chefele/SocialNetwork/download/social_test.txt"
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
    vout,vin=line.split(",")
    vout,vin=(int(vout),int(vin))
    vall[vin].append(vout)
    vall[vout].append(vin)
    vin_vout[vin].append(vout)
    vout_vin[vout].append(vin)
print "Done reading"

# count outdegress
outdegree_counts={}
for vout in vout_vin:
    outdegree=len(vout_vin[vout])
    if not(outdegree in outdegree_counts):
        outdegree_counts[outdegree]=0
    outdegree_counts[outdegree]+=1
print "done" 

report=[]
for outdegree_count in outdegree_counts:
    report.append((outdegree_count,outdegree_counts[outdegree_count]))
report.sort()

RESULTS_FILE="outdegree_hist.txt"
print "writing results to :",RESULTS_FILE
fout=open(RESULTS_FILE,"w")
for outdegree, freq in report:
    fout.write(str(outdegree)+","+str(freq)+"\n")
fout.close()

