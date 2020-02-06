CHIRP_DIR=../data/chirps

# should be a power of 2 plus 1
#SPEC_X=129
#SPEC_Y=129

SPEC_X=513
SPEC_Y=513

for infile in ${CHIRP_DIR}/*.aiff
do
    basefile=`basename ${infile} .aiff`
    specfile=${CHIRP_DIR}/${basefile}.png

    #echo sox ${infile} -n spectrogram -r -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
    #     sox ${infile} -n spectrogram -r -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
    echo sox ${infile} -n spectrogram        -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
         sox ${infile} -n spectrogram        -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 

    # sox spectrogram options are: 
    #   -m = monochrome / black-and-white
    #   -r = raw spectrogram with no axes
    #   -q N = N quantization / brightness levels 

done

