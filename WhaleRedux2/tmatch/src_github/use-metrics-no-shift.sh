# Because the some metrics files are so large (~1GB!), 
# it makes sense to just link to them rather than copy them.
# These scripts make it easy to reset the links 
# to the desired metrics set 
#

# workspace directory path
DIR=../workspace
cd ${DIR}

# get rid of old links
rm --verbose testMetrics.csv
rm --verbose trainMetrics.csv

# create links to original metrics data
ln --verbose --symbolic metrics-no-shift/testMetrics.csv  testMetrics.csv
ln --verbose --symbolic metrics-no-shift/trainMetrics.csv trainMetrics.csv


