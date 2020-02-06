
# clean out old files that will get refreshed; some may fail without harm
rm --verbose ../moby/corr32.csv ../moby/corr64.csv ../moby/testCorr32.csv ../moby/testCorr64.csv 
rm --verbose ../moby/testPredictions.csv ../moby/testPredictions.sub ../moby/trainPredictions.csv

stdbuf -o0 python driver.py 30 8

python reformatSubmission.py ../moby/testPredictions.sub ../moby/testPredictions.csv 

python ordering.py

stdbuf -o0 python driver.py 30 8

python reformatSubmission.py ../moby/testPredictions.sub ../moby/testPredictions.csv 

# now output to submit is in ../moby/testPredictions.csv


