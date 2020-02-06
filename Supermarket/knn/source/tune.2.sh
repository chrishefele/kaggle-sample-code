
KNNS='1 2 4 8 16 32 64 90 128 180 256 360 512 1024 4096'
DECAYDAYS1='1000000 2 8 32' 
DECAYDAYS2='1 4 16 64' 
FUNCS='median'
NTRAIN=90000
NTEST=10000
OUTDIR=/home/chefele/Supermarket/knn/logs

dayknn='--dayknn'
func=$FUNCS

for decaydays in $DECAYDAYS1
do
    outfile=$OUTDIR/knn-$dayknn-$decaydays-$func-$func.log 

    echo python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
    --centerfunc $func --predfunc $func \
    --ntrain $NTRAIN --ntest $NTEST \> $outfile \& 

    python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
    --centerfunc $func --predfunc $func \
    --ntrain $NTRAIN --ntest $NTEST > $outfile & 
done

echo
date
wait 


for decaydays in $DECAYDAYS2
do
    outfile=$OUTDIR/knn-$dayknn-$decaydays-$func-$func.log 

    echo python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
    --centerfunc $func --predfunc $func \
    --ntrain $NTRAIN --ntest $NTEST \> $outfile \& 

    python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
    --centerfunc $func --predfunc $func \
    --ntrain $NTRAIN --ntest $NTEST > $outfile & 
done

echo 
date

