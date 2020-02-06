# logistic-stop.csv - do logistic regression on stop values to predict start values

library(reshape)

TRAIN_FILE      <- '../download/train.csv'
TEST_FILE       <- '../download/test.csv'
SUB_TEMPLATE    <- '../download/sampleSubmission.csv'
SUB_OUTFILE     <- '../submissions/logistic-stop.csv'
PLOT_FILE       <- '../plots/logistic-stop.pdf'

NROWSAMPLES <- 1000 # each row has 400 elements in test, 800 in train

# Datafile format / columns: 
# train:        id, delta, start.1 ... start.400, stop.1 ... stop.400
# test:         id, delta, stop.1 ... stop.400
# submission:   id, start.1 ... start.400

meanAbsErr <- function(predictions, labels) {
    mean(abs(predictions-labels))
}

readFile <- function(filename) {
    cat('Reading: ', filename, '\n')
    read.csv(filename)
}

train <- readFile(TRAIN_FILE)

nTrainRows <- nrow(train)
cat('Sampling ', NROWSAMPLES,' out of ', nTrainRows, '\n')
sampleRows <- sample(nTrainRows, NROWSAMPLES)
train <- train[ sampleRows, ]

startCols <- paste("start.", 1:400, sep='')
stopCols  <- paste("stop.",  1:400, sep='')

# train:        id, delta, start.1 ... start.400, stop.1 ... stop.400
# test:         id, delta, stop.1 ... stop.400
# submission:   id, start.1 ... start.400
trainY <- melt.data.frame(train, c('id','delta'), startCols)
trainY <- trainY$value

trainX <- melt.data.frame(train, c('id','delta'), stopCols) 
trainX$variable <- NULL
stopValues <- trainX$value

cat('mean abs error, stop values\n')
print(meanAbsErr(trainY, stopValues))
cat('mean abs error, zero values\n')
print(meanAbsErr(trainY, 0*stopValues))

for(i in 0:1000) { 
    alpha <- i/1000.0
    prediction <- 1*( (alpha*stopValues) > runif(length(stopValues)) )
    cat('scale: ', alpha, ' mae: ', meanAbsErr(trainY, prediction),'\n')
}

stop()


