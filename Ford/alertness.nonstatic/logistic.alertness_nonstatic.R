# R logistic regression program for  
# "Stay Alert! The Ford Challenge" on Kaggle.com
# 1/20/2011 by Chris Hefele
#
# This program reads the test data, creates predictions for submission using
# cross-validated logistic regression, creates a ROC plot as well as an 
# AUC-vs-lambda(regularization) plot. 

library(glmnet)
library(caTools)

#TRAINING_FILE   <- "/home/chefele/Ford/download/fordTrain.csv"
TRAINING_FILE   <- "fordTrain.alertness_nonstatic_trials.csv"

TEST_FILE       <- "/home/chefele/Ford/download/fordTest.csv"

SUBMISSION_FILE <- "logistic.submission.alertness_nonstatic.csv"
PLOT_FILE       <- "logistic.plots.alertness_nonstatic.pdf"



LAMBDA          <- "lambda.1se"   # Regularization coef to use
                          # Use LAMBDA<-"lambda.min" for automatic lambda selection, 
                          # though lambda<-0.02 (~12 features) seems less overfit
USE_TRAIN_SAMPLES <- TRUE # TRUE=use random subset of training data; FALSE=use it all
NUM_TRAIN_SAMPLES <- 100000  # Samples to use if USE_TRAIN_SAMPLES<-TRUE
                          # Note: 604,329 rows in entire dataset 
ROC_PLOT_SAMPLES <- 10000  # Points to use for ROC curve plot

TIME_LAGS       <- c(0,1,2,4,8,16,32,64,128) # c(0,1,2,4,8,16,32,64,128) # lags to use for all variables 
RNG_SEED        <- 123  # random number generator seed 
set.seed(RNG_SEED)

# Define functions to select/transform the raw input data 
# into a form that's fed to the logistic regression
# Generally, try to transform histograms to something looking more Gaussian

logmin <- function(x) { 
    return( log(x-min(x)+1.0) ) 
}

make.X.dataframe <- function(x) {
    Xout <- data.frame( 
        logmin(x$P1),
        logmin(x$P2), #looks like high-freq noise (4 sample cycle); EEG? ZCR? LPFilter?
        logmin(x$P3),
        logmin(x$P4),
        logmin(x$P5),
        logmin(x$P6),
        x$P7,
        # x$P8, # ignore; all const 
        logmin(x$E1),
        x$E2,            # range 0-360, so something circular? steering wheel? 
        abs(x$E2-180.0), # lowers value if rotate in either direction
        x$E3,
        x$E4,
        x$E5,
        x$E6,
        logmin(x$E7),
        logmin(x$E8),
        x$E9,
        x$E10, # looks like speed! 25-80, lots at 70 exactly
        x$E11, 
        x$V1,
        x$V2,
        x$V3,
        logmin(x$V4),
        x$V5,
        x$V6,
        # x$V7, # ignore; all const
        x$V8,
        # x$V9, # ignore; all const
        x$V10,
        logmin(x$V11)
    )
    return(Xout) 
}

# Define functions for adding time lags of the data (stored in a dataframe)

lagcol <- function(the.col, the.lag) {     # timelag a vector of data
    end.index <- length(the.col) - the.lag
    padding <- rep( the.col[1], the.lag ) 
    return(  c( padding, the.col[1:end.index] ) )
}

lags.df <- function(df.in, lags) {   # create new dataframe with multiple lags
    df.out <- data.frame( dummy=1:nrow(df.in) ) #sets right dataframe size 
    for(col.name in names(df.in)) { 
        for(cur.lag in lags) {
            new.col.name <- paste( col.name, "_lag_", as.character(cur.lag), sep="" ) 
            df.out[[new.col.name]] <- lagcol( df.in[[col.name]], cur.lag )  
        }
    }
    df.out$dummy <- NULL 
    return( df.out ) 
}

absdiffs <- function(df.in, lags) {   # absolute value of any change
    df.out <- data.frame( dummy=1:nrow(df.in) ) # sets right dataframe size 
    for(col.name in names(df.in)) { 
        for(cur.lag in lags) {
            new.col.name <- paste( col.name, "_absdiffs_", as.character(cur.lag), sep="" ) 
            col.data <- df.in[[col.name]]
            if(cur.lag==0) { # special case to add original data; otherwise it would be 0's
                df.out[[new.col.name]] <- col.data
            } else {
                df.out[[new.col.name]] <- abs(col.data-lagcol(col.data,cur.lag))
            } 
        }
    }
    df.out$dummy <- NULL 
    return( df.out ) 
}


# OK, let's go. First, get & prep the data...

test  <- read.csv(TEST_FILE)
train <- read.csv(TRAINING_FILE)

X.test    <- cbind(
                #as.matrix( lags.df( make.X.dataframe(test),  TIME_LAGS ) ),
                as.matrix( absdiffs( make.X.dataframe(test),  TIME_LAGS ) )
             )

X.train   <- cbind(
                #as.matrix( lags.df( make.X.dataframe(train), TIME_LAGS ) ),
                as.matrix( absdiffs( make.X.dataframe(train), TIME_LAGS ) )
             )

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

