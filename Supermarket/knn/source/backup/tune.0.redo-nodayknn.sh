
KNNS='1 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192'
DECAYDAYS='1 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192'
FUNCS='mean median geomean rms'
NTRAIN=10000
NTEST=1000
OUTDIR=/home/chefele/Supermarket/knn/logs

for dayknn in ''
do

for decaydays in $DECAYDAYS
do

for centerfunc in $FUNCS
do

for predfunc in $FUNCS
do

outfile=$OUTDIR/knn-$dayknn-$decaydays-$centerfunc-$predfunc.log 

echo python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
--centerfunc $centerfunc --predfunc $predfunc \
--ntrain $NTRAIN --ntest $NTEST \> $outfile \& 

python knn.py --knns $KNNS $dayknn --decaydays $decaydays \
--centerfunc $centerfunc --predfunc $predfunc \
--ntrain $NTRAIN --ntest $NTEST > $outfile & 

echo

done

date
wait

done
done
done

