
cat makeFeaturesRsave.R | R --vanilla | tee makeFeaturesRsave.log

cat makeFeaturesCSV.R | R --vanilla 

mv *.csv ..

mv *.Rsave ..



