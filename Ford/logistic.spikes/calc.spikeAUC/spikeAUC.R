# calculate spike vs non-spike trial AUCs

library(ROCR)   # used to calcualate AUC

calcAUC <- function(predictions, labels) {
    # ROCR functions below
    performance( prediction(predictions,labels), "auc")@y.values[[1]] 
}

plotROC<- function(predictions, labels) {
    # ROCR functions below
    plot(
        performance( 
            prediction(predictions,labels), measure = "tpr", x.measure = "fpr" 
        )
    )
}


train       <- read.csv("../download/fordTrain.csv")
train.preds <- read.csv("pred.logistic.absdiffs.train.csv")

means <- tapply(train$P2,train$TrialID,mean)
SPIKE.THRESHOLD <- 12.5
spikeIDs <- as.integer(rownames( means[means>SPIKE.THRESHOLD]))

df <- data.frame(
        Prediction = train.preds$X1,
        IsAlert = train$IsAlert,
        SpikeTrial = train$TrialID %in% spikeIDs
      )

df.spike    <- df[ df$SpikeTrial,]
df.nonspike <- df[!df$SpikeTrial,] 

auc.spike    <- calcAUC(df.spike$Prediction,    df.spike$IsAlert)
auc.nonspike <- calcAUC(df.nonspike$Prediction, df.nonspike$IsAlert)
auc.all      <- calcAUC(df$Prediction,          df$IsAlert)

print(auc.spike)
print(auc.nonspike)
print(auc.all)

plotROC(df.spike$Prediction,    df.spike$IsAlert)
plotROC(df.nonspike$Prediction, df.nonspike$IsAlert)
plotROC(df$Prediction,          df$IsAlert)

