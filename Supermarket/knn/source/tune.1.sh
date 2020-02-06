
KNNS='1 2 4 8 16 32 64 90 128 180 256 360 512 1024'
DECAYDAYS='128 180 256 360'
FUNCS='median geomean'
NTRAIN=90000
NTEST=10000
OUTDIR=/home/chefele/Supermarket/knn/logs

dayknn='--dayknn'

for func in $FUNCS
do

  for decaydays in $DECAYDAYS
  do

    outfile=$OUTDIR/knn-$dayknn-$decaydays-$func-$func.log 

    echo python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
    --centerfunc $func --predfunc $func \
    --ntrain $NTRAIN --ntest $NTEST \> $outfile \& 

    python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
    --centerfunc $func --predfunc $func \
    --ntrain $NTRAIN --ntest $NTEST > $outfile & 

    echo

  done

date
echo
wait

done

