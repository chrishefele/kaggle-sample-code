library(glmnet)
library(ROCR)

TRAIN_FEATURES  <- '../features/leakage_features_train.csv'
TEST_FEATURES   <- '../features/leakage_features_test.csv'
PLOT_FILE       <- '../data/plots-logistic.pdf'
SUBMISSION_FILE <- '../submissions/submission-logistic.csv'

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

cat('\nReading data files\n')

train  <- read.csv(TRAIN_FEATURES)
train_labels <- train$whale_heard
train$whale_heard <- NULL
train$clip <- NULL

test <- read.csv(TEST_FEATURES)
test_clips <- test$clip
test$whale_heard <- NULL
test$clip  <- NULL

cat('Fitting model\n')
X.train <- as.matrix(train)
Y.train <- train_labels

system.time( 
    fit.train <- cv.glmnet(X.train, Y.train, type.measure="auc", family="binomial") 
)

# Output various stats & plots for analysis later...
coef(fit.train)
print(fit.train)
pdf(file=PLOT_FILE)
plot(fit.train)

# Write test set probability predictions to a file 
X.test     <- as.matrix(test)
prediction <- predict(fit.train, newx=X.test, type="response")
prediction <- as.data.frame(prediction)[["1"]]  # convert to vector

submission <- data.frame(clip=test_clips, probability=prediction)
write.csv(submission, file=SUBMISSION_FILE, row.names=FALSE, quote=FALSE)
cat("Wrote submission to:", SUBMISSION_FILE,"\n")

# Plot the ROC curve & estimate AUC against the training set 
Y.train.predictions <- predict(fit.train, newx=X.train, type="response")
auc <- calcAUC(Y.train.predictions, train_labels) 
plotROC(Y.train.predictions, train_labels, "ROC of Logistic Regression on LEAKAGE Features")

cat( "\n\n***** ROC AUC :", auc, "*****\n\n")
cat("Wrote plots to     :", PLOT_FILE,"\n")
cat("Wrote submission to:", SUBMISSION_FILE,"\n")

