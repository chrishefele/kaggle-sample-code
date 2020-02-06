library(infotheo)

PLOT_FILE   <- 'mutual-info-intrastart-image.pdf'
TRAIN_FILE  <- '../../download/train.csv'

pdf(file=PLOT_FILE)

# train: id, delta, start.1 ... start.400, stop.1 ... stop.400
train <- read.csv(TRAIN_FILE)

startCols <- paste("start.", 1:400, sep='')

for(d in sort(unique(train$delta))) {
    bitsStartCols   <- train[train$delta==d, startCols]
    mutInfos        <- natstobits(mutinformation(bitsStartCols))
    mutInfos        <- mutInfos[1:100,1:100] 
    mutInfos.log2   <- log(mutInfos)/log(2)
    mutInfos.diag0  <- 1*mutInfos
    diag(mutInfos.diag0)  <- 0
    mutInfosNorm    <- mutInfos / max(mutInfos)

    cat('delta: ', d, '  ')
    cat('mutual info log2 matrix (in bits)\n')
    print(signif(mutInfos.log2, digits=3))

    cat('\ndelta: ', d, '  ')
    cat('mutual information normalized to peak\n')
    print(signif(mutInfosNorm, digits=3))
    cat('\n\n')

    tag <- paste('Mutual Info log2  Matrix (delta=', d,')')
    image(mutInfos.log2,     main=tag)
    tag <- paste('Mutual Info diag0 Matrix (delta=', d,')')
    image(mutInfos.diag0,     main=tag)

}
