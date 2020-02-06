#!/bin/bash -v 

DATA_DIR=/home/chefele/SemiSupervised/data/data
TMP_DIR=/home/chefele/SemiSupervised/data/tmp
TRAIN_TEST_UNLABELED=$DATA_DIR/train+test+unlabeled_binary.csv

cat $TRAIN_TEST_UNLABELED | awk '{print $1}' > $TMP_DIR/lines  & 
cat $TRAIN_TEST_UNLABELED | awk '{print $2}' > $TMP_DIR/cols   &
wait

paste $TMP_DIR/lines $TMP_DIR/cols | awk '{print $0," 1"}'  > $TMP_DIR/ones  

echo -n > $TMP_DIR/zeros
for i in 1       # loops selected by trial and error; 1 provides at most 50% 1's, 50% 0's. 
do
    shuf $TMP_DIR/cols > $TMP_DIR/cols_shuf
    paste $TMP_DIR/lines $TMP_DIR/cols_shuf | awk '{print $0," 0"}' >> $TMP_DIR/zeros 
done

# Now we have to eliminate duplicates, as well as any conflicting lines
# e.g. (123 456 1)  AND (123 456 0) --- is (123, 456) a  1 or a 0?  
# First, sort files of ones & zeros data, so 1's always come first when line & cols match 
# Next, sort --unique drops any duplicates based on line & column only (fields 1 & 2)
# If have a duplicate with just a differing binary value (1 vs 0) we should always take the 1
# since zeros were randomly picked ; so the 1's are "true" points & are given priority
# These sorts take about an hour.

time cat $TMP_DIR/ones $TMP_DIR/zeros | \
sort --reverse --buffer-size=50% | \
sort --unique --key=1,2 --buffer-size=50% \
> $TMP_DIR/ones_zeros

# use line count for awk script below to split train & probe
wc $TMP_DIR/ones_zeros > $TMP_DIR/ones_zeros_wc 
cat $TMP_DIR/ones_zeros_wc


# now make bsvd train+probe file from ones and zeros data 

shuf $TMP_DIR/ones_zeros | awk '
BEGIN {  MIN_SUPPORT=2;  
         ALL_LINES=  149344933; # from ones_zeros_wc    
         TRAIN_LINES=140000000  # first N lines for training ; remainder is for probe/test
}
{   vout=1*$1; 
    vin =1*$2;
    if(NR<=TRAIN_LINES) {
        vout_counts[vout]++;
        vin_counts[  vin]++;
        print $1","$2","$3
    } else if((vout_counts[vout]>=MIN_SUPPORT) && 
              (vin_counts[  vin]>=MIN_SUPPORT)) { 
        print $1","$2","$3
    } else {
        skipped++; # note: skips lines in probe/test if vout or vin dont have enough pts in train
    }
}
' > $DATA_DIR/bsvd_train+probe.csv

cat $DATA_DIR/bsvd_train+probe.csv | awk 'NR <= 140000000' > $DATA_DIR/bsvd_train.csv  & 
cat $DATA_DIR/bsvd_train+probe.csv | awk 'NR >  140000000' > $DATA_DIR/bsvd_probe.csv  & 
wait 
echo "Done"

# TODO cleanup temp files 
