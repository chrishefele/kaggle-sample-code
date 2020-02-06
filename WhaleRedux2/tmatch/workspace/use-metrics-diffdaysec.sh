
# workspace directory path
DIR=.

# get rid of old links
rm --verbose ${DIR}/testMetrics.csv
rm --verbose ${DIR}/trainMetrics.csv

# make new links 
ln --verbose --symbolic ${DIR}/metrics-diffdaysec/testMetrics.csv  testMetrics.csv
ln --verbose --symbolic ${DIR}/metrics-diffdaysec/trainMetrics.csv trainMetrics.csv

