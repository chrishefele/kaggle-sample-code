
# Constants to configure

DATA_DIR=../data
DOWNLOAD_DIR=../download

TRAIN_FILE=${DOWNLOAD_DIR}/train_v2.txt
HOLDOUT_FILE=${DATA_DIR}/holdout.txt 

HOLDOUT_LENGTH=300000

# Create holdout file

echo `date`  Creating holdout file ${HOLDOUT_FILE}
tail --lines=${HOLDOUT_LENGTH} ${TRAIN_FILE} > ${HOLDOUT_FILE}

# Create ngram count files for the training set.
# ngram_mask is [n-gram length]+[word mask, 1 to include, 0 to exclude]
# e.g. 3+111 = create trigrams, and show all words in the trigram
#      3+101 = create trigrams, but only print first & last words (i.e. a skip-bigram)

for ngram_mask in 1+1 2+11 3+111 3+101 4+1111 4+1011 4+1101 5+11111 5+10111 5+11011 5+11101
do
    echo `date`  Processing training ngrams ${ngram_mask} 
    head --lines=-${HOLDOUT_LENGTH} ${TRAIN_FILE} | \
    ./ngramer ${ngram_mask} | \
    sort --parallel=4 | uniq -c |  sort -nr --parallel=4 \
    > ${DATA_DIR}/train_ngrams_${ngram_mask}.txt 
done

