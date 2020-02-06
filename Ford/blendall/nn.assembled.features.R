# Neural-Net blending of assembled features for the Ford data mining competition 
# 2/28/2011 by CJH

library(nnet)

library(ROCR)
# define function to calc AUC using ROCR library functions
calcAUC <- function(predictions, labels) {  
               performance(prediction(predictions,labels), "auc")@y.values[[1]] 
} 


TRAINING_FILE       <- "fordTrain.assembled.features.csv"
TEST_FILE           <- "fordTest.assembled.features.csv"
SUBMISSION_FILE_PREFIX  <- "ford.submission.nn."
SUBMISSION_FILE_SUFFIX  <- ".100_trials.csv"

#                     ****
HIDDEN_NODES        <- c(2,3,4,6,9,12,16,24) # hidden layer nodes to try; tunable 
MAX_ITERATIONS      <- 3000        # iterations for NN convergence
#                     ****

WRITE_PREDS         <- FALSE        # Write prediction file flag 
USE_TRAIN_SAMPLES   <- TRUE         # Leave as TRUE to save memory?
                                    # TRUE = use random subset of training data
                                    # FALSE = use it all (but not enough memory)

# NUM_TRAIN_SAMPLES   <- 300000     # Samples to use for training (when USE_TRAIN_SAMPLES<-TRUE)
                                    # Note: 604,329 rows in entire dataset 
                                    # Remainder in HOLDOUT set for AUC

#                   *****
TRAIN_START_TRIAL <- 1              # Train on a time-slice of the data; 
TRAIN_END_TRIAL   <- 100            # use 0-468 for full training? 469-479 missing, rest is validation set
#                   *****

RNG_SEED            <- 123          # random number generator seed 
set.seed(RNG_SEED)

# -------------------------------------------------------------------------

train   <- read.csv(TRAINING_FILE)
test    <- read.csv(TEST_FILE)

# remove headers so model doesn't try to use them  

train.fnames <-  setdiff( names(train), c("TrialID","ObsNum","IsAlert")) 
test.fnames  <-  setdiff( names(test),  c("TrialID","ObsNum","IsAlert"))  
X.train <- scale(as.matrix(train[train.fnames]))
X.test  <- scale(as.matrix(test[  test.fnames]))

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

# Create the neural net (runtime can be long, so time it & get verbose trace)
# ** Use softmax=TRUE or entropy=TRUE? 

for(hidden.nodes in HIDDEN_NODES) {
    print(paste("Using hidden nodes:",as.character(hidden.nodes)))

    print(system.time( 
        nn <- nnet( X.train, Y.train, size=hidden.nodes, 
                    entropy=TRUE, maxit=MAX_ITERATIONS) 
    ))

    # Write test set probability predictions to a file 
    if(WRITE_PREDS) {
        print("Writing predictions / submission file")
        nn.preds <- predict( nn, newdata=X.test, type="raw" )  
        Prediction <- nn.preds[,1]  #select column of probs for class 1
        TrialID <- test$TrialID
        ObsNum  <- test$ObsNum
        submission.data <- data.frame(TrialID, ObsNum, Prediction )
        submission.filename <- paste(SUBMISSION_FILE_PREFIX, as.character(hidden.nodes),"nodes",
                                     SUBMISSION_FILE_SUFFIX, sep="")
        write.csv(submission.data, file=submission.filename,
                  row.names=FALSE,col.names=TRUE,quote=FALSE)
    }

    # calculate & report AUC for training holdout set 
    nn.holdout.preds <- predict(nn, newdata=X.holdout, type="raw")
    Y.holdout.preds   <- nn.holdout.preds[,1] 
    holdout.AUC <- calcAUC(Y.holdout.preds, Y.holdout)
    print( paste( "Holdout set AUC: ",as.character(holdout.AUC) ))
    print(nn)   # print network config/stats 

} # for hidden.nodes
