
# clean out old files that will get refreshed; some may fail without harm
rm --verbose ../moby/corr32.csv ../moby/corr64.csv ../moby/testCorr32.csv ../moby/testCorr64.csv 
rm --verbose ../moby/testPredictions.csv ../moby/testPredictions.sub ../moby/trainPredictions.csv

# make sure we're linked to the old no-shift data (yields good CV score)
HERE=`pwd`
cd ../workspace
./use-metrics-no-shift.sh
ls -l 
cd $HERE

# create submission without using ordering feature files
stdbuf -o0 python driver.py 30 8
python reformatSubmission.py ../moby/testPredictions.sub ../moby/testPredictions.csv 

# now create ordering files from old no-shift data
python ordering.py

# switch train/test sets to add diffdaysec features
HERE=`pwd`
cd ../workspace
./use-metrics-diffdaysec.sh
ls -l 
cd $HERE

# create submission using ordering from no-shift features plus new test/train w diffdaysec
stdbuf -o0 python driver.py 30 8
python reformatSubmission.py ../moby/testPredictions.sub ../moby/testPredictions.csv 
stdbuf -o0 python submission.py

DIR=../submissions
cp --verbose *.sub  ${DIR}
cp --verbose ../moby/*Predictions.* ${DIR}

