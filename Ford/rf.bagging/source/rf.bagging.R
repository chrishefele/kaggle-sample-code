# Random-forest blending of assembled features on a sampled subset of trials 
# Written for the Ford data mining competition 3/4/2011 by CJH

library(randomForest)
library(ROCR)

TRAINING_FILE       <- "/home/chefele/Ford/blendall/fordTrain.assembled.features.csv"
TEST_FILE           <- "/home/chefele/Ford/blendall/fordTest.assembled.features.csv"

SUBMISSION_FILE     <- paste("/home/chefele/Ford/rf.bagging/predictions/",
                             "ford.submission.rf.",
                             format(Sys.time(),"%b%d-%H%M%S"),
                             ".csv", sep=""
                       )  # build timestamp into filename so it's unique  

#                     *****
TRAIN_TRIAL_SAMPLES <- 100          # number of trials to randomly sample 
#                     *****


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
if(TRUE) {

    sampled.TrialIDs <- sample( unique(train$TrialID), TRAIN_TRIAL_SAMPLES )  # *** NEW 
    sample.mask  <-  train$TrialID %in% sampled.TrialIDs
    holdout.mask <- !sample.mask 

    X.holdout <- X.train[holdout.mask,]
    Y.holdout <- Y.train[holdout.mask ]
    X.train   <- X.train[sample.mask,]
    Y.train   <- Y.train[sample.mask ]
}

print("Sampled Trial IDs being used:")
print(sampled.TrialIDs)
print( paste("Training on: ",as.character(nrow(X.train))," rows of data",sep="") )

# Create the random forest (runtime can be long, so time it & get verbose trace)

system.time( rf <- randomForest( X.train, as.factor(Y.train), proximity=FALSE, do.trace=TRUE) )

# Output various stats for analysis later...

print(rf)

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
print( paste("Holdout AUC: ", as.character(holdout.AUC),sep="") )  

# calculate AUC of out-of-bag predictions contained in randomForest object (rf), 
# (which is the default data used when predict is called without newdata=...)

rf.train.preds <- predict(rf, type="prob")
Y.train.preds   <- rf.train.preds[,"1"] 
OOB.AUC <- calcAUC( Y.train.preds, Y.train) 
print(OOB.AUC)  # out-of-bag AUC 


