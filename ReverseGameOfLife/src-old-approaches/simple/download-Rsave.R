
TRAIN_FILE      <- '../download/train.csv'
TEST_FILE       <- '../download/test.csv'
SUB_TEMPLATE    <- '../download/sampleSubmission.csv'
RSAVE_FILE      <- '../data/download.Rsave'

readFile<- function(filename) {
    cat('Reading: ', filename, '\n')
    read.csv(filename)
}

train <- readFile(TRAIN_FILE)
test  <- readFile(TEST_FILE)
sub   <- readFile(SUB_TEMPLATE)

cat('Writing : ', RSAVE_FILE, '\n')
save(train, test, sub, file=RSAVE_FILE)

cat('test load from : ', RSAVE_FILE, '\n')
loaded <- load(RSAVE_FILE)
cat('loaded the following objects: ',loaded)



