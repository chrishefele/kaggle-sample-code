
train=/home/chefele/Essay/download/release_3/training_set_rel3.tsv
num_topics=1,2,4,8,16,32,64,128,256

python cohesionFeatures.py $num_topics $train $train  try.training.csv 2>&1 | tee    try.log

