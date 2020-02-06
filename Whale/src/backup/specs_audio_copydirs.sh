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

