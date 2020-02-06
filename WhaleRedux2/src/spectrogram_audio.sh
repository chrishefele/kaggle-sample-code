OUTDIR=../data/spectrogram/all

# should be a power of 2 plus 1
SPEC_X=129
SPEC_Y=129
#SPEC_X=257
#SPEC_Y=257

for data_dir in 'train2' 'test2'
do
    for infile in ../download/${data_dir}/*.aif
    do
        basefile=`basename ${infile} .aif`
        specfile=${OUTDIR}/${basefile}.png

        echo sox ${infile} -n spectrogram -r -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
             sox ${infile} -n spectrogram -r -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
        #echo sox ${infile} -n spectrogram     -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 
        #     sox ${infile} -n spectrogram     -m -x ${SPEC_X} -y ${SPEC_Y} -o ${specfile} 

        # sox spectrogram options are: 
        #   -m = monochrome / black-and-white
        #   -r = raw spectrogram with no axes
        #   -q N = N quantization / brightness levels 
        #   -o outputfile

    done
done

ls ${OUTDIR} | grep TRAIN | 
awk '

    BEGIN { indir="../data/spectrogram/all/" } 

    /_0.png/ {  outdir="../data/spectrogram/train_nowhale/"
                print "cp --verbose "indir$0" "outdir$0 }
    
    /_1.png/ {  outdir="../data/spectrogram/train_whale/"
                print "cp --verbose "indir$0" "outdir$0 } 

' > _go_split_spectrograms.sh

chmod +x _go_split_spectrograms.sh
./_go_split_spectrograms.sh 
rm ./_go_split_spectrograms.sh

