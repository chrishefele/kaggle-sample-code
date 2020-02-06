library(NMFN)

TRAIN_FEATURES  <- '../features/image_features_train.csv' 
TEST_FEATURES   <- '../features/image_features_test.csv'
TRAIN_LABELS<- '../download/data/train.csv'

PLOT_FILE       <- 'pca_image_features.pdf'
pdf(file=PLOT_FILE)
par(mfrow=c(2,2))

cat('\nReading data files\n')
train <- read.csv(TRAIN_FEATURES)
train$clip_name <- NULL
labels <- read.csv(TRAIN_LABELS)$label

train <- train[labels==1,] # **** use 1=whale, 0=nowhale

print('Fitting PCA')
train_pca  <- prcomp(train)
prcomps <- train_pca$rotation

print('Plotting PCA components')
for(colnum in 1:ncol(prcomps)) {
    cat(as.character(colnum))
    cat(' ')
    prcomp <- prcomps[,colnum]
    n <- sqrt(length(prcomp))
    dim(prcomp) <- c(n,n)
    prcomp <- prcomp[,ncol(prcomp):1]

    tag <- paste('Principal Component',as.character(colnum))
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

