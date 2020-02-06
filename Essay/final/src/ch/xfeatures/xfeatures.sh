echo Remaking the xfeatures feature files

logfile=../../../logs/CH_xfeatures.log

train_infile=../../../data/training_set.tsv
valid_infile=../../../data/valid_set.tsv
test_infile=../../../data/test_set.tsv

train_outfile=../../../features/CH_xfeatures.training.csv 
valid_outfile=../../../features/CH_xfeatures.valid.csv
test_outfile=../../../features/CH_xfeatures.test.csv

date > $logfile

python xfeatures.py $train_infile  $train_outfile | tee -a $logfile
python xfeatures.py $valid_infile  $valid_outfile | tee -a $logfile
# python xfeatures.py $test_infile   $test_outfile  | tee -a $logfile

echo Done

