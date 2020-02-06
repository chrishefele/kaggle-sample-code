# Assemble a submission for the SemiSupervised Kaggle.com compeition
# CJH 10/17/2011
# Read in all the various feature files, run a SVM classifier, and output a submission file
# Adds PCA of analog variables
#
#------------------------------------------------------------------------------
#
# usage; 
# cat mk_sub_svm_pca.R | R --vanilla --args <bal|nobal>  <submissionfile>
#
args <- commandArgs(trailingOnly=TRUE)
BALANCE_DATA <- (args[1]=="bal")
SUBMISSION_FILE <- args[2]
print(BALANCE_DATA)
print(SUBMISSION_FILE)

ALL_ANALOGPCA <- "/home/chefele/SemiSupervised/data/data/train+test+unlabeled_analogpca.csv"

DIR_DOWNLOAD  <- "/home/chefele/SemiSupervised/download/competition_data/"
DIR_KMEANS    <- "/home/chefele/SemiSupervised/kmeans/data/"
DIR_DATA      <- "/home/chefele/SemiSupervised/data/data/"

TRAIN_ACTUALS <- paste(DIR_DOWNLOAD, "public_train.labels.dat", sep="")

TRAIN_KMEANS  <- paste(DIR_KMEANS,"full_kmeans.train.dense.dat",sep="") #del first col
TRAIN_ANALOG  <- paste(DIR_DATA,  "train_analog.csv",           sep="") 
TRAIN_BINARY  <- paste(DIR_DATA,  "bsvd_features_train.csv",    sep="") 

TEST_KMEANS   <- paste(DIR_KMEANS,"full_kmeans.test.dense.dat", sep="") # del first col
TEST_ANALOG   <- paste(DIR_DATA,  "test_analog.csv",            sep="") 
TEST_BINARY   <- paste(DIR_DATA,  "bsvd_features_test.csv",     sep="") 

#------------------------------------------------------------------------------

library(e1071)  #for svm
library(LiblineaR)  # for svd 
library(ROCR)

plotROC<- function(predictions, labels, plot.name) {
    # ROCR functions below
    plot(
        performance( 
            prediction(predictions,labels), measure = "tpr", x.measure = "fpr" 
        ), 
        main=plot.name
    )
}

calcAUC <- function(predictions, labels) {
    pred.tmp    <- prediction(predictions, labels) # ROCR function
    calc.AUC  <- performance(pred.tmp, "auc")@y.values[[1]] # ROCR function
    if(calc.AUC < 0.5) calc.AUC <- 1-calc.AUC
    return(calc.AUC) 
}

tagCols <- function(df, tag) { 
    names(df) <- paste(tag, names(df), sep="_")
    return(df)
}

filtBinary <- function(df) {
    return(data.frame(
        binary_V1 = df$binary_V1,
        binary_V2 = df$binary_V2,
        binary_V3 = df$binary_V3,
        binary_V4 = df$binary_V4,
        binary_V5 = df$binary_V5,
        binary_V6 = df$binary_V6,
        binary_V7 = df$binary_V7,
        binary_V8 = df$binary_V8,
        binary_V9 = df$binary_V9,
        binary_V10 = df$binary_V10,
        binary_V11 = df$binary_V11,
        binary_V12 = df$binary_V12,
        binary_V13 = df$binary_V13,
        binary_V14 = df$binary_V14,
        binary_V44 = df$binary_V44
    ))
}


#------------------------------------------------------------------------------
# Read & prepare the datasets 

indata <- read.csv(ALL_ANALOGPCA, header=FALSE)
prcomp.obj  <- prcomp( indata, scale=TRUE)
pcs <- data.frame(prcomp.obj$x)
train_analogpca <- pcs[    1: 50000,]      # TODO: define constants; 1:50k is train, 50k:100k is test, rest is ulabeled 
test_analogpca  <- pcs[50001:100000,]

train_actuals <- as.factor( read.csv(TRAIN_ACTUALS, header=FALSE)$V1 ) 

train_binary  <- filtBinary(tagCols( read.csv(TRAIN_BINARY, header=FALSE), "binary"))
test_binary   <- filtBinary(tagCols( read.csv(TEST_BINARY,  header=FALSE), "binary"))

train.df <- cbind( train_analogpca, train_binary )
test.df  <- cbind( test_analogpca,  test_binary  )
head(train.df)
head(test.df)

train <- as.matrix( train.df ) 
test  <- as.matrix( test.df  )

# FOR TESTING -- use a smaller sample
#NSAMP <- 2000
#train <- train[1:NSAMP,]
#test  <- test[ 1:NSAMP,]
#train_actuals <-train_actuals[1:NSAMP]

# constants used in data balancing
train_actuals_ones    <- table(train_actuals)["1"]
train_actuals_negones <- table(train_actuals)["-1"]


#------------------------------------------------------------------------------
# Fit SVM to transformed data

fit.svm <- NULL
if(BALANCE_DATA) {
    counts <- table(train_actuals)
    print("counts:")
    print(counts)
    ratio <- as.double(counts["1"])/as.double(counts["-1"])
    cwts <- c(  "-1"=ratio, "1"=1.0  )
    print("cwts:")
    print(cwts)
    system.time( fit.svm <-svm(train, train_actuals, kernel="linear",cost=1, probability=TRUE, class.weights=cwts) ) 
} else {
    system.time( fit.svm <-svm(train, train_actuals, kernel="linear",cost=1, probability=TRUE) ) 
}

print(fit.svm)
summary(fit.svm)

p <- predict(fit.svm, newdata=test, probability=TRUE)  
preds.test.svm <- attr(p, "probabilities")[,"1"]      # select prob of a "1" 

head(preds.test.svm)

zpadding <- mat.or.vec( nrow(test), max(1,100-ncol(test)) )

submission <- cbind( preds.test.svm, test, zpadding)
write.table(submission, file=SUBMISSION_FILE, sep=",", row.names=FALSE, col.names=FALSE, quote=FALSE)

