echo Remaking the cohesion feature files

logfile=../../../logs/CH_cohesionFeatures.log

train_infile=../../../data/training_set.tsv
valid_infile=../../../data/valid_set.tsv
test_infile=../../../data/test_set.tsv

train_outfile=../../../features/CH_cohesionFeatures.training.csv 
valid_outfile=../../../features/CH_cohesionFeatures.valid.csv
test_outfile=../../../features/CH_cohesionFeatures.test.csv

num_topics=2,4,8,256

date > $logfile

python cohesionFeatures.py $num_topics $train_infile  $train_infile $train_outfile 2>&1 | tee -a $logfile
python cohesionFeatures.py $num_topics $train_infile  $valid_infile $valid_outfile 2>&1 | tee -a $logfile
# python cohesionFeatures.py $num_topics $train_infile  $test_infile  $test_outfile  2>&1 | tee -a $logfile

echo Done

