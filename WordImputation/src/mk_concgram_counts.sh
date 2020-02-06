
# Constants to configure

DATA_DIR=../data
DOWNLOAD_DIR=../download
TRAIN_FILE=${DOWNLOAD_DIR}/train_v2.txt
HOLDOUT_LENGTH=300000

# Create concgram count files for the training set.
# ngram_mask is [n-gram length]+[word mask, 1 to include, 0 to exclude]
# 3+101 = create bi-concgrams from center word of trigrams and words outside of ngram

#for ngram_mask in 3+101 4+1011 4+1101 5+10111 5+11011 5+11101
for  ngram_mask in 3+101 4+1011 4+1101 
do
    echo `date`  Processing training concgrams ${ngram_mask} 
    head --lines=-${HOLDOUT_LENGTH} ${TRAIN_FILE} | \
    ./concgramer ${ngram_mask} | \
    ./ngramMapper  | \
    ./ngramReducer 20000000 | \
    sort --key=2 | \
    ./ngramReducer 1 | \
    sort -nr   > ${DATA_DIR}/train_concgrams_${ngram_mask}.txt 
done

