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

cat $DOWNLOAD/unlabeled_data.svmlight.dat  $DOWNLOAD/public_train_data.svmlight.dat > $DATA/concatenated_data.dat

# Step 2.  Learn the cluster centers.
$KMHOME/sofia-ml/sofia-kmeans \
  --k 100 \
  --opt_type mini_batch_kmeans \
  --dimensionality 1000001 \
  --training_file $DATA/concatenated_data.dat \
  --model_out $DATA/full_kmeans_model.txt \
  --iterations 10000 \
  --mini_batch_size 1000 \
  --objective_after_init \
  --objective_after_training \

# Step 3.  Apply the learned cluster centers to the training data.
$KMHOME/sofia-ml/sofia-kmeans \
  --model_in $DATA/full_kmeans_model.txt \
  --test_file $DOWNLOAD/public_train_data.svmlight.dat \
  --objective_on_test \
  --cluster_mapping_out $DATA/full_kmeans.train.dat \
  --cluster_mapping_type rbf_kernel \
  --cluster_mapping_param 0.01 \

# Step 4.  Apply the learned cluster centers to the test data.
$KMHOME/sofia-ml/sofia-kmeans \
  --model_in $DATA/full_kmeans_model.txt \
  --test_file $DOWNLOAD/public_test_data.svmlight.dat \
  --objective_on_test \
  --cluster_mapping_out $DATA/full_kmeans.test.dat \
  --cluster_mapping_type rbf_kernel \
  --cluster_mapping_param 0.01 \
 
# Step 5.  Create dense CSV format versions of the new data sets.
$SRC/svmlightToDenseFormat.pl $DATA/full_kmeans.train.dat > $DATA/full_kmeans.train.dense.dat
$SRC/svmlightToDenseFormat.pl $DATA/full_kmeans.test.dat  > $DATA/full_kmeans.test.dense.dat
 
# Step 6.  Execute the ./runLeaderboardEval.pl script.
cd $SRC 
pwd
$SRC/runLeaderboardEval.pl $DATA/full_kmeans.train.dense.dat $DOWNLOAD/public_train.labels.dat $DATA/full_kmeans.test.dense.dat $LIBSVM_DIR $DATA/test.full_kmeans.out


