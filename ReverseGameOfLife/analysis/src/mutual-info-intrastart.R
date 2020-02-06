library(infotheo)

PLOT_FILE <- 'mutual-info-intrastart.pdf'
TRAIN_FILE  <- '../../download/train.csv'
STOP_COL <- 'stop.272'
START_COL_ROOT <- 'start.272'

pdf(file=PLOT_FILE)
# par(mfrow=c(2,2))

# train: id, delta, start.1 ... start.400, stop.1 ... stop.400
train <- read.csv(TRAIN_FILE)

startCols <- paste("start.", 1:400, sep='')
stopCols  <- paste("stop.",  1:400, sep='')

for(d in sort(unique(train$delta))) {
    stopCol <- STOP_COL
    startColRoot <- START_COL_ROOT
    bitsStartCols <- train[train$delta==d, startCols]
    bitsStartColRoot   <- train[train$delta==d, startColRoot]

    #mutInfo.stopCol <- function(bitsStartCol) { 
    #    natstobits( mutinformation(bitsStopCol, bitsStartCol)) 
    #} 
    mutInfo.startColRoot <- function(bitsStartCol) { 
        natstobits( mutinformation(bitsStartColRoot, bitsStartCol)) 
    } 
    #mutInfos <- sapply(bitsStartCols, mutInfo.stopCol)
    mutInfos <- sapply(bitsStartCols, mutInfo.startColRoot)
    dim(mutInfos) <- c(20,20)
    
    cat('delta: ', d, '  ')
    cat('mutual information in bits\n')
    print(signif(mutInfos, digits=3))
    cat('\ndelta: ', d, '  ')
    cat('mutual information normalized to peak\n')
    mutInfosNorm <- mutInfos / max(mutInfos)
    print(signif(mutInfosNorm, digits=3))
    cat('\n\n')

    mxi <- max(mutInfos)
    mdi <- median(mutInfos)
    mni <- mean(mutInfos)
    se  <- entropy(bitsStartColRoot)
    cat('PEAK_STATS ', 'delta ',d, ' max ', mxi,' median ',mdi, ' mean ', mni)
    cat(' max/median ', mxi/mdi, ' max/mean ', mxi/mni,'\n')
    cat(' stop_entropy ', se, ' max/stop_entropy ', mxi/se,'\n')

    tag <- paste('Mutual Info between Start Cells & Start Cell 272 (delta=', d,')')
    image(mutInfos, main=tag)
    persp(mutInfos, xlab='board rows', ylab='board columns', 
          zlab='mutual information (bits)', zlim=c(0.001,0.120), 
          theta=30, phi=30, main=tag)
    mutInfos.sort <- sort(mutInfos, decreasing=TRUE)
    plot( mutInfos.sort, log='x', ylab='mutual info (bits)', 
         ylim=c(0.001,0.120), xlab='log rank', type='l', main=tag)
    plot( diff(mutInfos.sort), log='x', ylab='diff of mutual info (bits)', 
          xlab='log rank', type='l', main=paste('diff of',tag))


}
