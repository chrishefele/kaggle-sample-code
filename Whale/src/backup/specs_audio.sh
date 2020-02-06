OUTDIR=../data/spectrogram/all

# should be a power of 2 plus 1
#SPEC_X=129
#SPEC_Y=129

SPEC_X=257
SPEC_Y=257

for data_dir in 'train' 'test'
do
    for infile in ../download/data/${data_dir}/*.aiff
    do
        basefile=`basename ${infile} .aiff`
        specfile=${OUTDIR}/${basefile}.png

        #echo sox ${infile} -n spectrogram -r -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
        #     sox ${infile} -n spectrogram -r -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
        echo sox ${infile} -n spectrogram     -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
             sox ${infile} -n spectrogram     -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 

        # sox spectrogram options are: 
        #   -m = monochrome / black-and-white
        #   -r = raw spectrogram with no axes
        #   -q N = N quantization / brightness levels 

    done
done

