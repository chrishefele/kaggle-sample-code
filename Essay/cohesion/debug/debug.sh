# script to debug possible run-to-run variablity

train=/home/chefele/Essay/download/release_3/training_set_rel3.tsv
valid=/home/chefele/Essay/download/release_3/valid_set.tsv
valid_test=/home/chefele/Essay/final/data/valid+test_set.tsv

num_topics=2,4,8,256


python cohesionFeatures.py $num_topics $train $valid       CH_cohesionFeatures.valid_1.csv  2>&1 | tee -a CH_cohesionFeatures.valid_1.log  &
python cohesionFeatures.py $num_topics $train $valid       CH_cohesionFeatures.valid_2.csv  2>&1 | tee -a CH_cohesionFeatures.valid_2.log  &
python cohesionFeatures.py $num_topics $train $valid_test  CH_cohesionFeatures.valid_test.csv  2>&1 | tee -a CH_cohesionFeatures..valid_test.log  &

echo Waiting to finish 
wait
echo DONE

