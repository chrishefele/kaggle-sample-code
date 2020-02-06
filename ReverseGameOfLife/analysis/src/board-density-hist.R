
train <- read.csv('../../download/train.csv')
pdf(file='board-density-hist.pdf')

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

    startDensity <- rowSums(as.matrix(startVals))
    stopDensity  <- rowSums(as.matrix(stopVals))

    cat("\ndelta = ", delta.now,"\n")
    hist(startDensity,150)
    hist(stopDensity, 150)
}


