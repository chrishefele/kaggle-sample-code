# rf.sh <features_file>  <log_file>

featfile=$1
logfile=$2

cat rf.R | R --vanilla --args $featfile | tee $logfile

