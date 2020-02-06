# rf-qrf.sh <features_file>  <log_file>

featfile=$1
logfile=$2

cat rf-qrf.R | R --vanilla --args $featfile | tee $logfile

