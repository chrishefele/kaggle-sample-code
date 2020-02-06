library(NMFN)

TRAIN_FEATURES  <- '../features/image_features_train.csv' 
TEST_FEATURES   <- '../features/image_features_test.csv'
TRAIN_LABELS<- '../download/data/train.csv'

NUM_FEATURES <- 100 
NUM_FEATURES <- 10 

PLOT_FILE       <- 'nnmf_image_features.pdf'
pdf(file=PLOT_FILE)
par(mfrow=c(2,2))

cat('\nReading data files\n')
train <- read.csv(TRAIN_FEATURES)
train$clip_name <- NULL
labels <- read.csv(TRAIN_LABELS)$label

# TODO comment out line below to use all data
train <- train[labels==0,] # *** TODO use 1=whale, 0=nowhale

print('Fitting NNMF')
train_nnmf  <- nnmf(train, NUM_FEATURES)
prcomps <- train_nnmf$H

print('Plotting NNMF components')
for(rownum in 1:nrow(prcomps)) {
    cat(as.character(rownum))
    cat(' ')
    prcomp <- prcomps[rownum,]
    n <- sqrt(length(prcomp))
    dim(prcomp) <- c(n,n)
    prcomp <- prcomp[,ncol(prcomp):1]

    tag <- paste('Principal Component',as.character(rownum))
    # image(t(prcomp),main=tag)
    filled.contour(prcomp, plot.title=tag) # nlevels=??
}
cat('\n')

stop('Intentionally stopping before NNMF code')

#for(nfactors in c(1,2,5,10,20,50,100,200,400, 500, 1000, 2000)) { 
for(nfactors in c(400)) { 
    cat('\n*** Starting NNMF for ')
    cat(as.character(nfactors))
    cat(' factors\n')

    st <- system.time(
        train_nnmf <- nnmf(train, nfactors, maxiter=5000)
    )
    print(st)
    #image(train_nnmf$W)
    #image(train_nnmf$H)

}

