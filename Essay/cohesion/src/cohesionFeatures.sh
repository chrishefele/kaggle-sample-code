
train=/home/chefele/Essay/download/release_3/training_set_rel3.tsv
valid=/home/chefele/Essay/download/release_3/valid_set.tsv
#tests=   FILL IN TEST FILENAME HERE

num_topics=2,4,8,256

date > CH_cohesionFeatures.log  
python cohesionFeatures.py $num_topics $train $train  CH_cohesionFeatures.training.csv 2>&1 | tee -a CH_cohesionFeatures.log  
python cohesionFeatures.py $num_topics $train $valid  CH_cohesionFeatures.valid.csv    2>&1 | tee -a CH_cohesionFeatures.log  
#python cohesionFeatures.py $num_topics $train $tests CH_cohesionFeatures.test.csv     2>&1 | tee -a CH_cohesionFeatures.log 

