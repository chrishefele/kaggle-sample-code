library(glmnet)
library(ROCR)

# TRAIN_FEATURES <- '~/kaggle/WhaleRedux2/nmkridler/submissions/WR2-ordering-revised/trainPredictions.csv'
TRAIN_FEATURES <- '~/kaggle/WhaleRedux2/nmkridler/submissions/WR2-ordering-none/trainPredictions.csv'
PLOT_FILE       <- 'logistic-lags.pdf'
NLAGS           <- 100

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

lagFeatures <- function(labels, nlags) { 
    data.frame(embed(labels, nlags)) 
}

cat('\nReading data files\n')

# clip_name,labelTruth,label

train           <- read.csv(TRAIN_FEATURES)
train_preds     <- train$label
train_truth     <- train$labelTruth
train_features  <- lagFeatures(train_preds, NLAGS)
train_truth     <- train_truth[NLAGS:length(train_truth)]
# train_features$X1 <- NULL

cat('Fitting model\n')
X.train <- as.matrix(train_features)
Y.train <- train_truth

system.time( 
    fit.train <- cv.glmnet(X.train, Y.train, type.measure="auc", family="binomial") 
)

# Output various stats & plots for analysis later...
coef(fit.train)
print(fit.train)
pdf(file=PLOT_FILE)
plot(fit.train)

# Write test set probability predictions to a file 
#X.test     <- as.matrix(test)
#prediction <- predict(fit.train, newx=X.test, type="response")
#prediction <- as.data.frame(prediction)[["1"]]  # convert to vector
#submission <- data.frame(clip=test_clips, probability=prediction)
#write.csv(submission, file=SUBMISSION_FILE, row.names=FALSE, quote=FALSE)
#cat("Wrote submission to:", SUBMISSION_FILE,"\n")

# Plot the ROC curve & estimate AUC against the training set 
Y.train.predictions <- predict(fit.train, newx=X.train, type="response")
auc <- calcAUC(Y.train.predictions, train_truth) 
plotROC(Y.train.predictions, train_truth, "ROC of Logistic Regression on Features")

cat( "\n\n***** ROC AUC :", auc, "*****\n\n")
cat("Wrote plots to     :", PLOT_FILE,"\n")
#cat("Wrote submission to:", SUBMISSION_FILE,"\n")

# add ROC AUC of orignial predictions (1-dimension) for comparison? 
