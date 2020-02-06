library(reshape)

TRAIN_FILE  <- '../../download/train.csv'

#NROWSAMPLES <- 1000 # each row has 400 elements in test, 800 in train

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
#cat('Sampling ', NROWSAMPLES,' out of ', nTrainRows, '\n')
#sampleRows <- sample(nTrainRows, NROWSAMPLES)
#train <- train[ sampleRows, ]

startCols <- paste("start.", 1:400, sep='')
stopCols  <- paste("stop.",  1:400, sep='')

# train:        id, delta, start.1 ... start.400, stop.1 ... stop.400
# test:         id, delta, stop.1 ... stop.400
# submission:   id, start.1 ... start.400
trainY <- melt.data.frame(train, c('id','delta'), startCols)
startValues <- trainY$value
delta  <- trainY$delta 
#trainY <- trainY$value

trainX <- melt.data.frame(train, c('id','delta'), stopCols) 
trainX$variable <- NULL
stopValues <- trainX$value

df <- data.frame(stopValue=stopValues, startValue=startValues, delta=delta)
print(table(df))

