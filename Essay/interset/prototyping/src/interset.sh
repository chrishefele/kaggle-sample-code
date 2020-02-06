
featfile=../data/all_features_reduced.csv
logfile=interset.log

cat interset.R | R --vanilla --args $featfile | tee $logfile

