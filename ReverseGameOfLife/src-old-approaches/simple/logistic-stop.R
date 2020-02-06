# logistic-stop.csv - do logistic regression on stop values to predict start values

library(reshape)
library(glmnet)
library(ROCR)

TRAIN_FILE      <- '../download/train.csv'
TEST_FILE       <- '../download/test.csv'
SUB_TEMPLATE    <- '../download/sampleSubmission.csv'
SUB_OUTFILE     <- '../submissions/logistic-stop.csv'
PLOT_FILE       <- '../plots/logistic-stop.pdf'

NROWSAMPLES <- 1000 # each row has 400 elements in test, 800 in train

# Datafile format / columns: 
# train:        id, delta, start.1 ... start.400, stop.1 ... stop.400
# test:         id, delta, stop.1 ... stop.400
# submission:   id, start.1 ... start.400

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

meanAbsErr <- function(predictions, labels) {
    mean(abs(predictions-labels))
}

readFile <- function(filename) {
    cat('Reading: ', filename, '\n')
    read.csv(filename)
}

train <- readFile(TRAIN_FILE)

nTrainRows <- nrow(train)
cat('Sampling ', NROWSAMPLES,' out of ', nTrainRows, '\n')
sampleRows <- sample(nTrainRows, NROWSAMPLES)
train <- train[ sampleRows, ]

startCols <- paste("start.", 1:400, sep='')
stopCols  <- paste("stop.",  1:400, sep='')

# train:        id, delta, start.1 ... start.400, stop.1 ... stop.400
# test:         id, delta, stop.1 ... stop.400
# submission:   id, start.1 ... start.400
trainY <- melt.data.frame(train, c('id','delta'), startCols)
trainY <- trainY$value

trainX <- melt.data.frame(train, c('id','delta'), stopCols) 
trainX$variable <- NULL
# for debugging below
trainX$id <- NULL
trainX$delta <- NULL
stopValues <- trainX$value

cat(mean(trainY),'\n')
cat(mean(trainX$value),'\n')
print(head(trainX))
print(head(trainY))

cat('Fitting model\n')
system.time( 
    fit.train <- cv.glmnet( as.matrix(trainX), trainY, type.measure="auc", family="binomial") 
)

# Output various stats & plots for analysis later...
coef(fit.train)
print(fit.train)
pdf(file=PLOT_FILE)
plot(fit.train)

prediction <- predict(fit.train, as.matrix(trainX), type="response")
prediction <- as.data.frame(prediction)[["1"]]  # convert to vector
prediction <- 1*(prediction > runif(length(prediction)))

print(head(prediction))
print(sum(prediction))

cat('mean abs error, stop values\n')
print(meanAbsErr(trainY, stopValues))
cat('mean abs error, zero values\n')
print(meanAbsErr(trainY, 0*prediction))
cat('mean abs error, predicted values\n')
print(meanAbsErr(trainY, prediction))

stop()

remove(X.train)
remove(train)

test  <- readFile(TEST_FILE)
sub   <- readFile(SUB_TEMPLATE)


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



# oneStepRows <- test$delta == 1
# sub[ oneStepRows, startCols] <- test[oneStepRows, stopCols]
# sub[!oneStepRows, startCols] <- 0

write.csv(sub, file=OUTFILE, quote=FALSE, row.names=FALSE)


