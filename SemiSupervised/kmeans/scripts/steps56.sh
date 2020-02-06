#!/bin/bash -v

# Semi-Supervised challenge on Kaggle
# Instructions for creating K-means submission(s)
# Derived from instructions on this forum thread:
# http://www.kaggle.com/c/SemiSupervisedFeatureLearning/forums/t/902/benchmark-minibatch-k-means-step-by-step

# Step 1.  Combine the unlabled data set with the training data.
DOWNLOAD=/home/chefele/SemiSupervised/download/competition_data
SRC=/home/chefele/SemiSupervised/download/src
DATA=/home/chefele/SemiSupervised/kmeans/data
KMHOME=/home/chefele/SemiSupervised/kmeans
LIBSVM_DIR=/usr/bin

# Step 5.  Create dense CSV format versions of the new data sets.
$SRC/svmlightToDenseFormat.pl $DATA/full_kmeans.train.dat > $DATA/full_kmeans.train.dense.dat
$SRC/svmlightToDenseFormat.pl $DATA/full_kmeans.test.dat  > $DATA/full_kmeans.test.dense.dat
 
# Step 6.  Execute the ./runLeaderboardEval.pl script.
cd $SRC 
pwd
#$SRC/runLeaderboardEval.pl $DATA/full_kmeans.train.dense.dat $DOWNLOAD/public_train.labels.dat $DATA/full_kmeans.test.dense.dat $LIBSVM_DIR $DATA/test.full_kmeans.out
$SRC/fastRunLeaderboardEval.pl $DATA/full_kmeans.train.dense.dat $DOWNLOAD/public_train.labels.dat $DATA/full_kmeans.test.dense.dat $LIBSVM_DIR $DATA/test.full_kmeans.out


