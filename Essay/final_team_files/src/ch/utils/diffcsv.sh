# diffcsv.sh <file1.csv> <file2.csv>

file1=$1
file2=$2

cat diffcsv.R | R --vanilla --args $file1 $file2

