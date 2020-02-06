

printError <- function(preds, truth, tag) {
    err <- mean(colMeans(abs(preds-truth)))
    cat(tag, err, '\n')
}

train <- read.csv('../../download/train.csv')

id      <- train$id
delta   <- train$delta

startCols <- paste("start.", 1:400, sep='')
stopCols  <- paste("stop.",  1:400, sep='')
startVals <- train[startCols]
stopVals  <- train[stopCols]

for(delta.now in 1:5)  {

    rowMask <- delta == delta.now  
    startVals <- train[rowMask, startCols]
    stopVals  <- train[rowMask, stopCols]

    printError(preds=stopVals, truth=startVals, tag=paste("\n*** delta:", delta.now, "diff(start,stop)"))
    cat('startValues - stopValues breakdown:\n')
    diffs <- table(as.matrix(startVals - stopVals))
    cat('startValues - stopValues breakdown:\n')
    print(diffs)
    cat('startValues - stopValues breakdown (normalized):\n')
    print(diffs/sum(diffs))

}


