echo Remaking the xfeatures feature files

date > xfeatures.log 
python xfeatures.py /home/chefele/Essay/download/release_3/training_set_rel3.tsv  xfeatures.training.csv | tee -a xfeatures.log
python xfeatures.py /home/chefele/Essay/download/release_3/valid_set.tsv          xfeatures.valid.csv    | tee -a xfeatures.log 
# python xfeatures.py /home/chefele/Essay/download/release_3/test_set.tsv          xfeatures.test.csv     | tee -a xfeatures.log 

cp xfeatures.training.csv CH_xfeatures.training.csv 
cp xfeatures.valid.csv    CH_xfeatures.valid.csv    
# cp xfeatures.test.csv     CH_xfeatures.test.csv     

