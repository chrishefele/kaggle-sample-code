# parseFeatures.sh <infile> <outfile> <logfile>

#infile=parseEssays.tsv
#outfile=parseFeatures.csv

infile=$1
outfile=$2
logfile=$3

jython parseFeatures.py $infile $outfile | tee $logfile

