library(infotheo)

PLOT_FILE <- 'mutual-info-ranks-plot.pdf'
TRAIN_FILE  <- '../../download/train.csv'
STOP_COL <- 'stop.272'

pdf(file=PLOT_FILE)
# par(mfrow=c(2,2))
plot(   c(),log='x', ylab='mutual info (bits)', 
        ylim=c(0.001,0.120), xlim=c(1,400), xlab='log rank', type='l', main="ranked start board mutual infos with stop")

# train: id, delta, start.1 ... start.400, stop.1 ... stop.400
train <- read.csv(TRAIN_FILE)

startCols <- paste("start.", 1:400, sep='')
stopCols  <- paste("stop.",  1:400, sep='')

for(d in sort(unique(train$delta))) {
    stopCol <- STOP_COL
    bitsStartCols <- train[train$delta==d, startCols]
    bitsStopCol   <- train[train$delta==d, stopCol]

    mutInfo.stopCol <- function(bitsStartCol) { 
        natstobits( mutinformation(bitsStopCol, bitsStartCol)) 
    } 
    mutInfos <- sapply(bitsStartCols, mutInfo.stopCol)
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
    se  <- entropy(bitsStopCol)
    cat('PEAK_STATS ', 'delta ',d, ' max ', mxi,' median ',mdi, ' mean ', mni)
    cat(' max/median ', mxi/mdi, ' max/mean ', mxi/mni,'\n')
    cat(' stop_entropy ', se, ' max/stop_entropy ', mxi/se,'\n')

    tag <- paste('delta:', d)
    #image(mutInfos, main=tag)
    #persp(mutInfos, theta=30, phi=30, main=tag)
    #line(sort(mutInfos, decreasing=TRUE),log='x', ylab='mutual info (bits)', 
    #     ylim=c(0,0.12), xlab='log rank', type='b', main=tag)

    lines(sort(mutInfos, decreasing=TRUE))

}
