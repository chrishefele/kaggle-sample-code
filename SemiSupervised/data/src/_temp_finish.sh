#!/bin/bash -v 

DATA_DIR=/home/chefele/SemiSupervised/data/data

cat $DATA_DIR/bsvd_train+probe.csv | awk 'NR <= 140000000' > $DATA_DIR/bsvd_train.csv  & 
cat $DATA_DIR/bsvd_train+probe.csv | awk 'NR >  140000000' > $DATA_DIR/bsvd_probe.csv  & 
wait 
echo "Done"

