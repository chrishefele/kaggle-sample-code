# Random-forest based blending of assembled features for the Ford data mining competition 2/28/2011 by CJH

library(randomForest)
library(caTools)
library(ROCR)

TRAINING_FILE       <- "fordTrain.assembled.features.csv"
TEST_FILE           <- "fordTest.assembled.features.csv"
SUBMISSION_FILE     <- "ford.submission.rf.csv"
PLOT_FILE           <- "ford.plots.rf.pdf"

USE_TRAIN_SAMPLES   <- TRUE         # Leave as TRUE for for random forest
                                    # TRUE = use random subset of training data
                                    # FALSE = use it all (but not enough memory)

# NUM_TRAIN_SAMPLES   <- 100000       # Samples to use (when USE_TRAIN_SAMPLES<-TRUE)
                                    # Note: 604,329 rows in entire dataset 
                                    # If >100000, starts swapping with 8GB 

#                   *****
TRAIN_START_TRIAL <- 1              # sequential time slice for training
TRAIN_END_TRIAL   <- 100            # 0-468 for full training? not enough memory
#                   *****


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

# Create the random forest (runtime can be long, so time it & get verbose trace)

system.time( rf <- randomForest( X.train, as.factor(Y.train), proximity=FALSE, do.trace=TRUE) )


# Output various stats & plots for analysis later...

print(rf)
pdf(file=PLOT_FILE)
plot(rf)

# Write test set probability predictions to a file 

rf.preds <- predict( rf, newdata=X.test, type="prob" )  # calcs probs for each class ("0" & "1")
Prediction <- rf.preds[,"1"]  #select column of probs for class "1"
TrialID <- test$TrialID
ObsNum  <- test$ObsNum
submission.data <- data.frame(TrialID, ObsNum, Prediction )
write.csv(submission.data, file=SUBMISSION_FILE, row.names=FALSE,col.names=TRUE,quote=FALSE)


# define function to calc AUC using ROCR library functions

calcAUC <- function(predictions, labels) {  
    performance(prediction(predictions,labels), "auc")@y.values[[1]] 
} 

# go calculate AUC for training holdout set 

rf.holdout.preds <- predict(rf, newdata=X.holdout, type="prob")
Y.holdout.preds   <- rf.holdout.preds[,"1"] 
holdout.AUC <- calcAUC(Y.holdout.preds, Y.holdout)
print(holdout.AUC)  # training set holdout AUC

# calculate AUC of out-of-bag predictions contained in randomForest object (rf), 
# (which is the default data used when predict is called without newdata=...)

rf.train.preds <- predict(rf, type="prob")
Y.train.preds   <- rf.train.preds[,"1"] 
OOB.AUC <- calcAUC( Y.train.preds, Y.train) 
print(OOB.AUC)  # out-of-bag AUC 


