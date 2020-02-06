# features_plot.sh <features_file> > <plot_file> 

infile=$1
plotfile=$2

cat features_plot.R | R --vanilla --args $infile $plotfile

