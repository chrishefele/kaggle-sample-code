feature_file_dir=../../../features
output_dir=../../../features
log_file=../../../logs/CH_intersetFeatures.log

cat intersetFeatures.R | R --vanilla --args $feature_file_dir $output_dir | tee $log_file

