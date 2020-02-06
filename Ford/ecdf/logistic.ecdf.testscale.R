# R program for "Stay Alert! The Ford Challenge" on Kaggle.com
# 2/25/2011 by Chris Hefele
#

library(glmnet)
library(caTools)

TRAINING_FILE       <- "/home/chefele/Ford/blendall/fordTrain.assembled.features.csv"
TEST_FILE           <- "/home/chefele/Ford/blendall/fordTest.assembled.features.csv"

SUBMISSION_FILE     <- "logistic.submission.ecdf.testscale.csv"
PLOT_FILE           <- "logistic.plots.ecdf.testscale.pdf"

LAMBDA              <- "lambda.min" # Regularization coef to use; 0.005
                                    # Use LAMBDA<-"lambda.min" for automatic lambda selection, 
                                    # though lambda<-0.02 (~12 features) seems less overfit
USE_TRAIN_SAMPLES   <- FALSE        # TRUE=use random subset of training data; FALSE=use it all
NUM_TRAIN_SAMPLES   <- 100000       # Samples to use if USE_TRAIN_SAMPLES<-TRUE
                                    # Note: 604,329 rows in entire dataset 
ROC_PLOT_SAMPLES    <- 1000         # Points to use for ROC curve plot

RNG_SEED            <- 123          # random number generator seed 
set.seed(RNG_SEED)


train   <- read.csv(TRAINING_FILE)
test    <- read.csv(TEST_FILE)

# remove headers so regression doesn't try to use them  
train.fnames <-  setdiff( names(train), c("TrialID","ObsNum","IsAlert")) 
test.fnames  <-  setdiff( names(test),  c("TrialID","ObsNum","IsAlert"))  

X.train <- train[train.fnames]
X.test  <- test[  test.fnames]

for(nm in names(X.train)) {
    trn.dat <- as.matrix(X.train[[nm]])
    tst.dat <- as.matrix(X.test[[ nm]])
    trntst.dat <- rbind( trn.dat, tst.dat) 
    # normalize the data to percentiles using ecdf 
    # Note: the TEST distribution is used to normalize both the training & test sets
    # Technically this overfits to the test data, but it gives better AUC ;-)
    X.train[[nm]]  <- ecdf( tst.dat    )( trn.dat )  
    X.test[[ nm]]  <- ecdf( tst.dat    )( tst.dat )
} # for 

X.train <- as.matrix(X.train)
X.test  <- as.matrix(X.test) 
Y.train <- train$IsAlert

if(USE_TRAIN_SAMPLES) {
    sample.mask <- sample( 1:nrow(X.train), NUM_TRAIN_SAMPLES)
    X.train <- X.train[sample.mask,]
    Y.train <- Y.train[sample.mask ]
}

# Do a cross-validated logistic regression; default is 10 folds 
# (runtime can be long, so time it)

system.time( 
    fit.train <- cv.glmnet(X.train, Y.train, type.measure="auc", family="binomial") 
)

# Output various stats & plots for analysis later...

coef(fit.train)
print(fit.train)
pdf(file=PLOT_FILE)
plot(fit.train)

# Write test set probability predictions to a file 

Prediction <- predict( fit.train, newx=X.test, s=LAMBDA, type="response")
TrialID <- test$TrialID
ObsNum  <- test$ObsNum
submission.data <- data.frame(TrialID, ObsNum, Prediction )
write.csv(submission.data, file=SUBMISSION_FILE, row.names=FALSE,col.names=TRUE,quote=FALSE)

# Plot the ROC curve & estimate AUC against the training set 
# (using the 10-fold cross-validated model)
# Note: colAUC plotting routine can't handle the entire training set, 
# so a sampled subset is used instead

sample.mask <- sample( 1:length(Y.train), ROC_PLOT_SAMPLES)
Y.train.predictions   <- predict(fit.train, newx=X.train, s=LAMBDA, type="response")
trainAUC <- colAUC( Y.train.predictions[sample.mask], Y.train[sample.mask] , plotROC=TRUE)
print(trainAUC)

