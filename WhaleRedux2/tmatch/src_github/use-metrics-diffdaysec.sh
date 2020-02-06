
# workspace directory path
DIR=../workspace

cd ${DIR}

# get rid of old links
rm --verbose testMetrics.csv
rm --verbose trainMetrics.csv

# make new links 
ln --verbose --symbolic metrics-diffdaysec/testMetrics.csv  testMetrics.csv
ln --verbose --symbolic metrics-diffdaysec/trainMetrics.csv trainMetrics.csv

