# Reads in features, runs SVM, outputs file for submission

library(e1071)  # for SVM
BALANCE_DATA = TRUE #***** FLAG for data balancing

SUBMISSION_FILE <- "submission.csv"

TRAIN_ACTUALS <- "/home/chefele/SemiSupervised/download/competition_data/public_train.labels.dat"
train_actuals <- as.factor( read.csv(TRAIN_ACTUALS, header=FALSE)$V1 ) 

train <- as.matrix( read.csv("features_for_svm_train.csv") )
test  <- as.matrix( read.csv("features_for_svm_test.csv")  )

fit.svm <- NULL
if(BALANCE_DATA) {
    counts <- table(train_actuals)
    cwts <- c(  "-1"=(1.0*counts["1"]/counts["-1"]), "1"=1.0  )
    system.time( fit.svm <-svm(train, train_actuals, kernel="linear",cost=1, probability=TRUE, class.weights=cwts) ) 
} else {
    system.time( fit.svm <-svm(train, train_actuals, kernel="linear",cost=1, probability=TRUE) ) 
}

print(fit.svm)
summary(fit.svm)

p <- predict(fit.svm, newdata=test, probability=TRUE)  
preds.test.svm <- attr(p, "probabilities")[,"1"]      # select prob of a "1" 

head(preds.test.svm)

zpadding <- mat.or.vec( nrow(test), 100-ncol(test))

submission <- cbind( preds.test.svm, test, zpadding)
write.table(submission, file=SUBMISSION_FILE, sep=",", row.names=FALSE, col.names=FALSE, quote=FALSE)

