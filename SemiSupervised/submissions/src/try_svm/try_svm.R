library(e1071)

N<-10000

train_actuals <- as.factor(sample(0:1, N, replace=TRUE))
train <- data.frame(a=runif(N),b=runif(N))
test  <- data.frame(a=runif(N),b=runif(N))

train_actuals
train
test

system.time( fit.svm <-svm(train, train_actuals, kernel="linear",cost=1, probability=TRUE) ) 
print(fit.svm)
summary(fit.svm)

p <- predict(fit.svm, newdata=test, probability=TRUE)  # TODO: how to select preds? What's returned?
preds.test.svm <- attr(p, "probabilities")[,"1"]

p

preds.test.svm

zpadding <- mat.or.vec( nrow(test), 10-ncol(test))

submission <- cbind( preds.test.svm, test, zpadding)
write.table(submission, file="try_svm.csv", sep=",", row.names=FALSE, col.names=FALSE, quote=FALSE)


