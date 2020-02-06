OUTDIR=../data/wav

for train_test in 'train' 'test'
do
    for infile in ../download/data/${train_test}/*.aiff
    do
        basefile=`basename ${infile} .aiff`
        outfile=${OUTDIR}/${train_test}/${basefile}.wav
             sox ${infile} ${outfile} 
        echo sox ${infile} ${outfile} 
    done
done

