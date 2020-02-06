library(glmnet)
library(ROCR)

TRAIN_LABELS    <- '../download/data/train.csv'
TRAIN_FEATURES  <- '../features/file_features_train.csv' 
TEST_FEATURES   <- '../features/file_features_test.csv'
PLOT_FILE       <- 'logistic.pdf'
SUBMISSION_FILE <- 'logistic.csv'

CV_FOLDS        <- 10 


calcAUC <- function(predictions, labels) {  # uses ROCR library
                pred <- prediction(predictions, labels)
                auc.tmp <- performance(pred,"auc")
                auc <- as.numeric(auc.tmp@y.values)
                return(auc)
}

plotROC<- function(predictions, labels, plot.name) {
    # ROCR functions below
    plot(
        performance( 
            prediction(predictions, labels), measure = "tpr", x.measure = "fpr" 
        ), 
        main=plot.name
    )
}

print('Reading data files')
train  <- read.csv(TRAIN_FEATURES)
train$clip_name <- NULL

duplicate_mask <- train$duplicate == 1

# TODO added below for testing 
train2 <- read.csv('../features/chirp_features_train.csv')
train3 <- read.csv('../features/fft_features_train.csv')
train2$clip_name <- NULL
train3$clip_name <- NULL
train <- cbind(train, train2, train3)

labels <- read.csv(TRAIN_LABELS)$label
labels <- labels[1:nrow(train)] # for when a smaller set of training features is used for testing

train_wts            <- 0*labels 
# modify weights to provide class balance
train_wts[labels==1] <- 1
train_wts[labels==0] <- sum(labels==1) / sum(labels==0)
# don't train on duplicates
train_wts[duplicate_mask] <- 0  
print(sum(train_wts))
print(head(train_wts,30))

#test   <- read.csv(TEST_FEATURES)
#test$clip_name  <- NULL

print('Fitting model')
X.train <- as.matrix(train)
Y.train <- labels
cv_fold <- c( 0:(nrow(train)-1) ) %% CV_FOLDS + 1
system.time( 
    fit.train <- cv.glmnet(X.train, Y.train, type.measure="auc", family="binomial", foldid=cv_fold, weights=train_wts) 
)

# Output various stats & plots for analysis later...
coef(fit.train)
print(fit.train)
pdf(file=PLOT_FILE)
plot(fit.train)

# Write test set probability predictions to a file 

#   X.test <- as.matrix(test)
#   prediction <- predict( fit.train, newx=X.test, type="response")
#   submission.data <- data.frame(prediction)
#   write.csv(submission.data, file=SUBMISSION_FILE, row.names=FALSE,col.names=FALSE)

# Plot the ROC curve & estimate AUC against the training set 

Y.train.predictions <- predict(fit.train, newx=X.train, type="response")
print("Original AUC")
print( calcAUC(Y.train.predictions, labels) ) 
plotROC(Y.train.predictions, labels, "ROC of logistic regression on features")


new.preds <- as.vector(Y.train.predictions)
new.preds[duplicate_mask] <- labels[duplicate_mask]
print("Estimated AUC with copied labels")
print( calcAUC(new.preds, labels) ) 
plotROC(new.preds, labels, "ROC of logistic regression on features, with some copied labels")

