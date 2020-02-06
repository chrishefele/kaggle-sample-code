
# clean out old files that will get refreshed; some may fail without harm
rm --verbose ../moby/corr32.csv ../moby/corr64.csv ../moby/testCorr32.csv ../moby/testCorr64.csv 
rm --verbose ../moby/testPredictions.csv ../moby/testPredictions.sub ../moby/trainPredictions.csv

# create submission without using ordering feature files
stdbuf -o0 python driver.py 30 8
python reformatSubmission.py ../moby/testPredictions.sub ../moby/testPredictions.csv 
stdbuf -o0 python submission.py

DIR=../submissions/WR2-ordering-none
cp --verbose *.sub  ${DIR}
cp --verbose ../moby/*Predictions.* ${DIR}

# now create ordering files
python ordering.py
# create submission with using ordering feature files
stdbuf -o0 python driver.py 30 8
python reformatSubmission.py ../moby/testPredictions.sub ../moby/testPredictions.csv 
stdbuf -o0 python submission.py

DIR=../submissions/WR2-ordering-revised
cp --verbose *.sub  ${DIR}
cp --verbose ../moby/*Predictions.* ${DIR}

