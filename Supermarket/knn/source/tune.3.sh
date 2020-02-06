
KNNS='1 2 4 8 16 32 64 90 128 180 256 360 512 1024 4096'
DECAYDAYS='8' 
FUNCS='median'
NTRAIN=90000
NTEST=10000
OUTDIR=/home/chefele/Supermarket/knn/logs
RAND_SEEDS='1234567 42 3 1024'

dayknn='--dayknn'
func=$FUNCS
decaydays=$DECAYDAYS

for rand_seed in $RAND_SEEDS 
do
    outfile=$OUTDIR/knn-$dayknn-$decaydays-$func-$func-rseed-$rand_seed.log 

    echo python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
    --centerfunc $func --predfunc $func \
    --ntrain $NTRAIN --ntest $NTEST --randseed $rand_seed \> $outfile \& 

    python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
    --centerfunc $func --predfunc $func \
    --ntrain $NTRAIN --ntest $NTEST --randseed $rand_seed > $outfile & 
done

echo
date
wait 
date

