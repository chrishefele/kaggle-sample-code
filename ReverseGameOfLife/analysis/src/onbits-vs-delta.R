
TRAIN_FILE  <- '../../download/train.csv'

# train: id, delta, start.1 ... start.400, stop.1 ... stop.400
train <- read.csv(TRAIN_FILE)
startCols <- paste("start.", 1:400, sep='')
stopCols  <- paste("stop.",  1:400, sep='')

for(d in sort(unique(train$delta))) {
    df.start <- train[train$delta==d, startCols]
    df.stop  <- train[train$delta==d, stopCols ]
    cat('delta: ', d)
    cat(' mean_startbits: ', mean(colMeans(df.start)))
    cat(' mean_stopbits : ', mean(colMeans(df.stop)))
    cat('\n')
}

