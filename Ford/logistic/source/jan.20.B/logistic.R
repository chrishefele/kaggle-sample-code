# R logistic regression program for  
# "Stay Alert! The Ford Challenge" on Kaggle.com
# 1/20/2011 by Chris Hefele
#
# This program reads the test data, creates predictions for submission using
# cross-validated logistic regression, creates a ROC plot as well as an 
# AUC-vs-lambda(regularization) plot. 

library(glmnet)
library(caTools)

TRAINING_FILE   <- "/home/chefele/Ford/download/fordTrain.csv"
TEST_FILE       <- "/home/chefele/Ford/download/fordTest.csv"
SUBMISSION_FILE <- "logistic.submission.csv"
PLOT_FILE       <- "logistic.plots.pdf"

LAMBDA          <- 0.02   # Regularization coef to use
                          # Use LAMBDA<-"lambda.min" for automatic lambda selection, 
                          # though lambda<-0.02 (~12 features) seems less overfit
USE_TEST_SAMPLES<- FALSE  # TRUE=use random subset of training data; FALSE=use it all
NUM_TEST_SAMPLES<- 20000  # Samples to use if USE_TEST_SAMPLES<-TRUE
                          # Note: 604,329 rows in entire dataset 
ROC_PLOT_SAMPLES<- 10000  # Points to use for ROC curve plot

# Define a function to select/transform the raw input data 
# into a form that's fed to the logistic regression

make.X.matrix <- function(x) {
    Xout <- data.frame( 
        x$ObsNum,sqrt(x$ObsNum), 
        x$P1,x$P2,x$P3,x$P4,x$P5,x$P6,x$P7,x$P8,
        x$E1,x$E2,x$E3,x$E4,x$E5,x$E6,x$E7,x$E8,x$E9,x$E10,x$E11,
        x$V1,x$V2,x$V3,x$V4,x$V5,x$V6,x$V7,x$V8,x$V9,x$V10,x$V11
    )
    Xm <- as.matrix(Xout)
    return(Xm)
}


# OK, let's go. First, get & prep the data...

test  <- read.csv(TEST_FILE)
train <- read.csv(TRAINING_FILE)
if(USE_TEST_SAMPLES) {
    sample.mask <- sample( 1:nrow(train), NUM_TEST_SAMPLES)
    train <- train[sample.mask,]
}
X.test  <- make.X.matrix(test)
X.train <- make.X.matrix(train)
Y.train <- train$IsAlert

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
ObsNum <- test$ObsNum
submission.data <- data.frame(TrialID, ObsNum, Prediction )
write.csv(submission.data, file=SUBMISSION_FILE, row.names=FALSE,col.names=TRUE)

# Plot the ROC curve & estimate AUC against the training set 
# (using the 10-fold cross-validated model)
# Note: colAUC plotting routine can't handle the entire training set, 
# so a sampled subset is used instead

sample.mask <- sample( 1:length(Y.train), ROC_PLOT_SAMPLES)
Y.train.predictions   <- predict(fit.train, newx=X.train, s=LAMBDA, type="response")
trainAUC <- colAUC( Y.train.predictions[sample.mask], Y.train[sample.mask] , plotROC=TRUE)
print(trainAUC)

