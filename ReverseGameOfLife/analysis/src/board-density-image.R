
train <- read.csv('../../download/train.csv')
pdf(file='board-density-image.pdf')
par(mfrow=c(2,2))

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

    for(density in c(1:15)*10) {
        cat("\ndelta = ", delta.now," density: ", density,"\n")
        density.mask <- (startDensity > density-10) & (startDensity <= density)
        startVals.density <- startVals[density.mask,]
        x <- colMeans(as.matrix(startVals.density))
        dim(x) <- c(20,20)
        nboards <- nrow(startVals.density)
        tag <- paste('numAlive:', as.character(density), 'delta:', as.character(delta.now), "boards:",as.character(nboards))
        image(x, main=tag)
        persp(x, xlab='board rows', ylab='board columns', zlab='alive probability', 
                    zlim=range(0,0.5), theta=30, phi=30, main=tag) 
        persp(x, xlab='board rows', ylab='board columns', zlab='alive probability', 
                    zlim=range(0,0.5), theta=30, phi=30, main=tag) 
        image(x, main=tag)
    }
}

