OUTDIR=../data/spectrogram/all

# should be a power of 2 plus 1
SPEC_X=129
SPEC_Y=129

#SPEC_X=257
#SPEC_Y=257

for data_dir in 'train' 'test'
do
    for infile in ../download/data/${data_dir}/*.aiff
    do
        basefile=`basename ${infile} .aiff`
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

cat ../download/data/train.csv | sed 's/\./ /g' | sed 's/,/ /g' | 
awk '
    { 
        if($3==0) {
            outdir="../data/spectrogram/train_nowhale/"
        } else {
            outdir="../data/spectrogram/train_whale/"
        }
        indir="../data/spectrogram/all/"
        print "cp --verbose "indir$1".png "outdir$1".png"
    }
' > _go_split_spectograms.sh

chmod +x _go_split_spectograms.sh
./_go_split_spectograms.sh
rm ./_go_split_spectograms.sh

