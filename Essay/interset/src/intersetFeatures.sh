feature_file_dir=/home/chefele/Dropbox/essay/final/features
output_dir=.
log_file=intersetFeatures.log

cat intersetFeatures.R | R --vanilla --args $feature_file_dir $output_dir | tee $log_file


