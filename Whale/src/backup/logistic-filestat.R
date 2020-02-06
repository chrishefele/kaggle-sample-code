library(glmnet)
library(ROCR)

TRAIN_LABELS    <- '../download/data/train.csv'
# TRAIN_FEATURES  <- '../features/chirp_features_train_3000.csv' # TODO *** 3000 for testing 
TRAIN_FEATURES  <- '../features/filestat_features_train.csv' 
TEST_FEATURES   <- '../features/filestat_features_test.csv'
PLOT_FILE       <- 'logistic.pdf'
SUBMISSION_FILE <- 'logistic.csv'


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

labels <- read.csv(TRAIN_LABELS)$label
labels <- labels[1:nrow(train)] # for when a smaller set of training features is used for testing

#test   <- read.csv(TEST_FEATURES)
#test$clip_name  <- NULL

print('Fitting model')
X.train <- as.matrix(train)
Y.train <- labels
system.time( 
    fit.train <- cv.glmnet(X.train, Y.train, type.measure="auc", family="binomial") 
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

print( calcAUC(Y.train.predictions, labels) ) 

plotROC(Y.train.predictions, labels, "ROC of logistic regression on features")




