#!/bin/bash -v

DOWNLOAD=/home/chefele/SemiSupervised/download/competition_data
DATA_DIR=/home/chefele/SemiSupervised/data/data
TEMP_DIR=/home/chefele/SemiSupervised/data/tmp

cat  \
$DOWNLOAD/public_train_data.svmlight.dat \
$DOWNLOAD/public_test_data.svmlight.dat \
$DOWNLOAD/unlabeled_data.svmlight.dat \
> $DATA_DIR/train+test+unlabeled_data.svmlight.dat


