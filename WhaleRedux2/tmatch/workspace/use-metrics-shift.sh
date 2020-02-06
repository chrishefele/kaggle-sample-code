# use-shift-metrics.sh
# use-no-shift-metrics.sh
#
# Because the shifted metrics files are so large (~1GB!), 
# it makes sense to just link to them rather than copy them.
# These scripts make it easy to reset the links 
# to the desired metrics set (either shifted or not shifted)
#

# workspace directory path
DIR=.

# get rid of old links
rm --verbose ${DIR}/testMetrics.csv
rm --verbose ${DIR}/trainMetrics.csv

# create links to original metrics data
# ln --verbose --symbolic ${DIR}/metrics-no-shift/testMetrics.csv  testMetrics.csv
# ln --verbose --symbolic ${DIR}/metrics-no-shift/trainMetrics.csv trainMetrics.csv

# create links to shifted metrics data (with leads/lags of metrics)
ln --verbose --symbolic ${DIR}/metrics-shift/testMetrics.csv  testMetrics.csv
ln --verbose --symbolic ${DIR}/metrics-shift/trainMetrics.csv trainMetrics.csv

