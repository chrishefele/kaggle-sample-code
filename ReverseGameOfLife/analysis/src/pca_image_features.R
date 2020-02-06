library(NMFN)

TRAIN_FEATURES  <- '../../download/test.csv'
PLOT_FILE       <- 'pca_image_features.pdf'

pdf(file=PLOT_FILE)
par(mfrow=c(2,2))

cat('\nReading data files\n')
train_raw <- read.csv(TRAIN_FEATURES)
train_raw$id <- NULL

for(nDelta in 1:5) {
    train <- train_raw[train_raw$delta==nDelta,]
    train$delta <- NULL
    cat('Fitting PCA for delta:', nDelta, '\n')
    # train <- t(as.matrix(train)) # TODO remove? 
    train_pca  <- prcomp(train)
    prcomps    <- train_pca$rotation

    print('Plotting PCA components')
    for(colnum in 1:100) {
        cat(as.character(colnum))
        cat(' ')
        prcomp <- prcomps[,colnum]
        n <- sqrt(length(prcomp))
        dim(prcomp) <- c(n,n)
        prcomp <- prcomp[,ncol(prcomp):1]

        tag <- paste('PrComp:',as.character(colnum), 'Delta:',as.character(nDelta))
        # image(t(prcomp),main=tag)
        filled.contour(prcomp, plot.title=tag) # nlevels=??
    }
    cat('\n')
}

