# Assemble a submission for the SemiSupervised Kaggle.com compeition
# CJH 10/14/2011
# Read in all the various feature files, run a SVM classifier, and output a submission file
#
#------------------------------------------------------------------------------
#
# usage; 
# cat mk_sub_svm.R | R --vanilla --args <bal|nobal>  <filt|nofilt> <submissionfile>
#
args <- commandArgs(trailingOnly=TRUE)
BALANCE_DATA <- (args[1]=="bal")
FILTER_VARS<- (args[2]=="filt") # select strong variables (found by LR & L1 regularization)
SUBMISSION_FILE <- args[3]
print(BALANCE_DATA)
print(FILTER_VARS)
print(SUBMISSION_FILE)


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

# select variables with non-zero weights in a LR using L1 regularization
filterVars <- function(df) {
  df_out <- data.frame( 
    kmeans_V2 = df$kmeans_V2,
    kmeans_V6 = df$kmeans_V6, kmeans_V12 = df$kmeans_V12, kmeans_V14 = df$kmeans_V14,
    kmeans_V19 = df$kmeans_V19, kmeans_V21 = df$kmeans_V21, kmeans_V26 = df$kmeans_V26,
    kmeans_V31 = df$kmeans_V31, kmeans_V46 = df$kmeans_V46, kmeans_V48 = df$kmeans_V48,
    kmeans_V50 = df$kmeans_V50, kmeans_V53 = df$kmeans_V53, kmeans_V55 = df$kmeans_V55,
    kmeans_V59 = df$kmeans_V59, kmeans_V61 = df$kmeans_V61, kmeans_V72 = df$kmeans_V72,
    kmeans_V74 = df$kmeans_V74, kmeans_V77 = df$kmeans_V77, kmeans_V80 = df$kmeans_V80,
    kmeans_V82 = df$kmeans_V82, kmeans_V84 = df$kmeans_V84, kmeans_V85 = df$kmeans_V85,
    kmeans_V87 = df$kmeans_V87, kmeans_V90 = df$kmeans_V90, kmeans_V91 = df$kmeans_V91,
    kmeans_V97 = df$kmeans_V97,
    analog_V2 =  df$analog_V2,   analog_V4 = df$analog_V4, analog_V6 = df$analog_V6,
    analog_V8 =  df$analog_V8,   analog_V11 = df$analog_V11, analog_V13 = df$analog_V13,
    analog_V14 = df$analog_V14, analog_V16 = df$analog_V16, analog_V17 = df$analog_V17,
    analog_V19 = df$analog_V19, analog_V20 = df$analog_V20, analog_V21 = df$analog_V21,
    analog_V22 = df$analog_V22, analog_V28 = df$analog_V28, analog_V29 = df$analog_V29,
    analog_V30 = df$analog_V30, analog_V32 = df$analog_V32, analog_V33 = df$analog_V33,
    analog_V35 = df$analog_V35, analog_V37 = df$analog_V37, analog_V39 = df$analog_V39,
    analog_V40 = df$analog_V40, analog_V41 = df$analog_V41, analog_V42 = df$analog_V42,
    analog_V44 = df$analog_V44, analog_V45 = df$analog_V45, analog_V46 = df$analog_V46,
    binary_V2 =  df$binary_V2, binary_V3 = df$binary_V3, binary_V4 = df$binary_V4,
    binary_V6 =  df$binary_V6, binary_V8 = df$binary_V8, binary_V9 = df$binary_V9,
    binary_V10 = df$binary_V10, binary_V11 = df$binary_V11, binary_V12 = df$binary_V12,
    binary_V13 = df$binary_V13, binary_V14 = df$binary_V14, binary_V44 = df$binary_V44
  )
  return(df_out)
}


#------------------------------------------------------------------------------
# Read & prepare the datasets 

train_actuals <- as.factor( read.csv(TRAIN_ACTUALS, header=FALSE)$V1 ) 

train_kmeans  <- tagCols( read.csv(TRAIN_KMEANS, header=FALSE), "kmeans")
train_analog  <- tagCols( read.csv(TRAIN_ANALOG, header=FALSE), "analog")
train_binary  <- tagCols( read.csv(TRAIN_BINARY, header=FALSE), "binary")

test_kmeans   <- tagCols( read.csv(TEST_KMEANS,  header=FALSE), "kmeans")
test_analog   <- tagCols( read.csv(TEST_ANALOG,  header=FALSE), "analog")
test_binary   <- tagCols( read.csv(TEST_BINARY,  header=FALSE), "binary")

# delete first column, which is a constant 0 placeholder 
train_kmeans$kmeans_V1 <- NULL
test_kmeans$kmeans_V1  <- NULL

train.df <- cbind( train_kmeans, train_analog, train_binary )
test.df  <- cbind( test_kmeans,  test_analog,  test_binary  )

if(FILTER_VARS) {
    train.df <- filterVars(train.df)
    test.df  <- filterVars(test.df)
} 

train <- as.matrix( train.df ) 
test  <- as.matrix( test.df  )

# FOR TESTING -- use a smaller sample
# NSAMP <- 2000
# train <- train[1:NSAMP,]
# test  <- test[ 1:NSAMP,]
# train_actuals <-train_actuals[1:NSAMP]

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

