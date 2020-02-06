# library(e1071)
library(LiblineaR)

library(ROCR)
plotROC<- function(predictions, labels, plot.name) {
    # ROCR functions below
    plot(
        performance(
            prediction(predictions,labels), measure = "tpr", x.measure = "fpr"
        ),
        main=plot.name
    )
}

calcAUC <- function(predictions, labels) {
    pred.tmp    <- prediction(predictions, labels) # ROCR function
    calc.AUC  <- performance(pred.tmp, "auc")@y.values[[1]] # ROCR function
    if(calc.AUC < 0.5) calc.AUC <- 1-calc.AUC
    return(calc.AUC)
}


DIR <- "/home/chefele/SemiSupervised/download/competition_data/"

train<-as.matrix(read.csv( paste(DIR, "example_transform.public_train_data.csv",sep=""), header=FALSE))
test <-as.matrix(read.csv( paste(DIR, "example_transform.public_test_data.csv",sep=""), header=FALSE))

y_df <-read.csv(paste(DIR,"public_train.labels.dat", sep=""), header=FALSE)
y    <-y_df$V1

train_scaled<- scale(train, center=TRUE, scale=TRUE)

model_type <- 0
# 0 = L2 reg logistic regression
# 6 = L1 reg logistic regression
# 1 = L2 reg L2 loss SVM (dual)
# 2 = L2 reg L2 loss SVM (primal)
# 3 = L2 reg L1 loss SVM (dual)
# 5 = L1 reg L2 loss SVM

model <- LiblineaR(data=train_scaled, labels=y, type=model_type, cost=1, bias=TRUE, cross=0, verbose=TRUE)

test_scaled<- scale(test, attr(train_scaled,"scaled:center"), attr(train_scaled,"scaled:scale"))
predict_result <- predict(model, test_scaled, proba=FALSE, decisionValues=TRUE, cross=0)
decvals <- predict_result$decisionValues
predvals<- predict_result$predictions

print("AUC:")
print(calcAUC(predvals, y))

head(decvals)



