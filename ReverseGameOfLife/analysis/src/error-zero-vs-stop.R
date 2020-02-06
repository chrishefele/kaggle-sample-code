

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
zeroVals  <- 0 * stopVals 

printError(preds=zeroVals, truth=startVals, tag="overall predict zero err:")
printError(preds=stopVals, truth=startVals, tag="overall predict stop err:")
cat('\n')

for(delta.now in 1:5)  {

    rowMask <- delta == delta.now  
    startVals <- train[rowMask, startCols]
    stopVals  <- train[rowMask, stopCols]
    zeroVals  <- 0 * stopVals 

    printError(preds=zeroVals, truth=startVals, tag=paste(delta.now, "step predict zero err:"))
    printError(preds=stopVals, truth=startVals, tag=paste(delta.now, "step predict stop err:"))
    cat('\n')
}


