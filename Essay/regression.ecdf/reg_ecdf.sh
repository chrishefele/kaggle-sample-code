# reg_ecdf.sh <features_file>  <log_file>

featfile=$1
logfile=$2

cat reg_ecdf.R | R --vanilla --args $featfile | tee $logfile

