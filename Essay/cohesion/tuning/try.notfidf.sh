
train=/home/chefele/Essay/download/release_3/training_set_rel3.tsv
valid=/home/chefele/Essay/download/release_3/valid_set.tsv
#tests=   FILL IN TEST FILENAME HERE

num_topics=1,2,4,8,16,32,64,128,256

python cohesionFeatures_notfidf.py $num_topics $train $train  CH_cohesionFeatures_notfidf.training.csv   2>&1 | tee    CH_cohesionFeatures_notfidf.log &  

python cohesionFeatures.py         $num_topics $train $train  CH_cohesionFeatures_withtfidf.training.csv 2>&1 | tee    CH_cohesionFeatures_withtfidf.log  &  


