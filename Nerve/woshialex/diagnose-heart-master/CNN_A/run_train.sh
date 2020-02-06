#!/bin/bash
#Ntrain=500;
Ntrain=1140;

##### preprocess the data for the CNN to train
##### we prepare two different image size to train
THEANO_FLAGS='device=cpu' ./preprocess.py 196
THEANO_FLAGS='device=cpu' ./preprocess.py 256

####run all version of the net with different parameters
for version in 3 5 6 7 10 11 12 13
do
	#set the parameters
	cp config_v"$version".py config.py
	#train a network to predict contours based on sunnybrook data and hand labeled data
	./train_net.py
	#forecast the contours for all the cases
	./predict_net.py 1 $Ntrain
done

####generate a sex_age information file
./get_sex_age.py 1 $Ntrain
