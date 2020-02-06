# parseEssays.sh  <infile> <outfile> <logfile> 
#
# Parsing essays is time consuming, so run several instances in parallel,
# each parsing a different essay set ('eset') and writing to a seperate file,
# then concatenating those files after all parsing completes. 

#infile=/home/chefele/Essay/download/release_3/training_set_rel3.tsv
#outfile=parseEssays.tsv

infile=$1
outfile=$2
logfile=$3

# note: esets below should appear in alphabetical order, and be consecutive so can concat them later
#       e.g.  1 2 3 4 5 6,  or 12 34 56, or 123456, but NOT 62 14 53
for eset in 1 2 3 4 5 6 7 8 
do
    echo jython parseEssays.py $infile $eset parseEssays.$eset.tsv \> parseEssays.$eset.log  2\>\&1  \&
         jython parseEssays.py $infile $eset parseEssays.$eset.tsv  > parseEssays.$eset.log  2>&1     & 
done

echo Started  parsing at `date`
wait
echo Finished parsing at `date`

# Now consolidate the results (note, in alphabetical order!)
cat parseEssays.?.tsv > $outfile
rm  parseEssays.?.tsv

cat parseEssays.?.log > $logfile
rm  parseEssays.?.log

echo Parsing results written to $outfile
echo Logfile         written to $logfile

