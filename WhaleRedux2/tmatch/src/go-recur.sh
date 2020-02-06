
# clean out old files that will get refreshed; some may fail without harm
rm --verbose ../moby/corr32.csv ../moby/corr64.csv ../moby/testCorr32.csv ../moby/testCorr64.csv 
rm --verbose ../moby/testPredictions.csv ../moby/testPredictions.sub ../moby/trainPredictions.csv

# create submission without using ordering feature files
stdbuf -o0 python driver.py 30 8
python reformatSubmission.py ../moby/testPredictions.sub ../moby/testPredictions.csv 
# stdbuf -o0 python submission.py

DIR=../submissions/WR2-recur
cp --verbose *.sub  ${DIR}
cp --verbose ../moby/*Predictions.* ${DIR}

for loop in 1 2 3 4 5 6 7 8 9 
do 
    echo RECUR_LOOP ${loop}
    # now create ordering files
    python ordering.py
    # create submission with using ordering feature files
    stdbuf -o0 python driver.py 30 8
    python reformatSubmission.py ../moby/testPredictions.sub ../moby/testPredictions.csv 
    # stdbuf -o0 python submission.py
done

DIR=../submissions/WR2-recur
cp --verbose *.sub  ${DIR}
cp --verbose ../moby/*Predictions.* ${DIR}

