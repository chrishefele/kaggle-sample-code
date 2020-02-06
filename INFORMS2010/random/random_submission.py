# Generate a random submission for the INFORMS 2010 contest
import random
fout = open("random_submission.csv", "w")
for line in open("../data/ResultData.csv"):
    tokens = line.split(",")
    if "Timestamp" in tokens[0]:
        fout.write(tokens[0]+","+"TargetVariable\n")
    else: 
        timestamp = str(round(float(tokens[0]),5))
        timestamp = timestamp.strip()
        fout.write(timestamp+","+str(random.random())+"\n")
