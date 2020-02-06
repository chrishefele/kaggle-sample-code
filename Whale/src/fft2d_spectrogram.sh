
INDIR=../data/spectrogram/train_whale
OUTDIR=../data/spectrogram.fft/train_whale

for f in $INDIR/train100??.png
do
    bf=`basename $f`
    echo ${f}
    python fft2d.py $INDIR/${bf}  $OUTDIR/fft2d-${bf} 
done



INDIR=../data/spectrogram/train_nowhale
OUTDIR=../data/spectrogram.fft/train_nowhale

for f in $INDIR/train100??.png
do
    bf=`basename $f`
    echo ${f}
    python fft2d.py $INDIR/${bf}  $OUTDIR/fft2d-${bf} 
done

