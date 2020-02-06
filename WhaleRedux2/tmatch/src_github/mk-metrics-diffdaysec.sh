
# add columns with the new metrics to the columns of the current metrics

echo creating test metrics file by appending diffdaysec metrics 
paste -d, testMetrics.csv  ../../features/diff_daysec_features_test.csv  > metrics-diffdaysec/testMetrics.csv

echo creating train metrics file by appending diffdaysec metrics 
paste -d, trainMetrics.csv ../../features/diff_daysec_features_train.csv > metrics-diffdaysec/trainMetrics.csv

