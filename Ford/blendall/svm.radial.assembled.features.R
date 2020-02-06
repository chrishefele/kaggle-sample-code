# SVM based blending of assembled features for the Ford data mining competition 2/28/2011 by CJH

library(e1071)
library(caTools)
library(ROCR)

TRAINING_FILE       <- "fordTrain.assembled.features.csv"
TEST_FILE           <- "fordTest.assembled.features.csv"
SUBMISSION_FILE     <- "ford.submission.svm.radial.csv"


USE_TRAIN_SAMPLES   <- TRUE         # Leave as TRUE for for SVM
                                    # TRUE = use random subset of training data
                                    # FALSE = use it all (but not enough memory)

#                   *****
TRAIN_START_TRIAL <- 1              # sequential time slice for training
TRAIN_END_TRIAL   <- 100            # 0-468 for full training? not enough memory
#                   *****

LINEAR_KERNEL     <- FALSE          # pick either linear or radial, not both 
RADIAL_KERNEL     <- !LINEAR_KERNEL # (note: add & tune gamma with radial kernel?)

RNG_SEED            <- 123          # random number generator seed 
set.seed(RNG_SEED)

# -------------------------------------------------------------------------

train   <- read.csv(TRAINING_FILE)
test    <- read.csv(TEST_FILE)

# remove headers so regression doesn't try to use them  

train.fnames <-  setdiff( names(train), c("TrialID","ObsNum","IsAlert")) 
test.fnames  <-  setdiff( names(test),  c("TrialID","ObsNum","IsAlert"))  
X.train <- as.matrix(train[train.fnames])
X.test  <- as.matrix(test[  test.fnames])

# partition data into holdout & training subsets, chosen via random sampling 

Y.train <- train$IsAlert
if(USE_TRAIN_SAMPLES) {

    sample.mask  <-  train$TrialID %in% (TRAIN_START_TRIAL:TRAIN_END_TRIAL) #sequential time slice 
    holdout.mask <- !sample.mask 

    X.holdout <- X.train[holdout.mask,]
    Y.holdout <- Y.train[holdout.mask ]
    X.train   <- X.train[sample.mask,]
    Y.train   <- Y.train[sample.mask ]
}

# fit the SVM  (runtime can be long, so time it & get verbose trace)

if(LINEAR_KERNEL) {
    system.time( fit.svm <- svm(X.train,Y.train,kernel="linear",cost=1,probability=TRUE) )
}
if(RADIAL_KERNEL) {
    system.time( fit.svm <- svm(X.train,Y.train,kernel="radial",cost=1,probability=TRUE) ) # gamma=? use default
}

# Output various stats & plots for analysis later...

print(fit.svm)

# Write test set probability predictions to a file 

svm.preds <- predict( fit.svm, newdata=X.test, probability=TRUE )  
Prediction <- svm.preds
TrialID <- test$TrialID
ObsNum  <- test$ObsNum
submission.data <- data.frame(TrialID, ObsNum, Prediction )
write.csv(submission.data, file=SUBMISSION_FILE, row.names=FALSE,col.names=TRUE,quote=FALSE)


# define function to calc AUC using ROCR library functions

calcAUC <- function(predictions, labels) {  
    performance(prediction(predictions,labels), "auc")@y.values[[1]] 
} 

# go calculate AUC for training holdout set 

svm.holdout.preds <- predict(fit.svm, newdata=X.holdout, probability=TRUE)
Y.holdout.preds   <- svm.holdout.preds
holdout.AUC <- calcAUC(Y.holdout.preds, Y.holdout)
print(holdout.AUC)
print( paste("Holdout AUC: ",as.character(holdout.AUC),sep="") )  # training set holdout AUC



