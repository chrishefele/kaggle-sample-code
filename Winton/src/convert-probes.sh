
INDIR=../probes/test1
OUTDIR=../probes/test2

for f in ${INDIR}/*.csv
do
    fbase=`basename ${f}`
    infile=${INDIR}/${fbase} 
    outfile=${OUTDIR}/t2${fbase}
    echo python convert-submission.py ${infile} ${outfile}
         python convert-submission.py ${infile} ${outfile}
done

