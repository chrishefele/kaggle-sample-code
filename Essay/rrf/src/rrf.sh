# rrf.sh <features_file>  <log_file>

featfile=$1
logfile=$2

cat rrf.R | R --vanilla --args $featfile | tee $logfile

