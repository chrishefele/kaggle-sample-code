# plot histograms of the kmeans example 100 feature variables 

TRAIN         <- "/home/chefele/SemiSupervised/download/competition_data/example_transform.public_train_data.csv"
TRAIN_ACTUALS <- "/home/chefele/SemiSupervised/download/competition_data/public_train.labels.dat"
TAG           <- "kmeans"

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

train            <- read.csv(TRAIN,        header=FALSE)
train_actuals_df <- read.csv(TRAIN_ACTUALS,header=FALSE)
train_actuals    <- train_actuals_df$V1

pdf("feature_kmeans_plots.pdf")
par(mfrow=c(2,2))   # (Rows,Cols) layout of multiple plots per page 

for(varName in names(train)) {
    print(varName)
    hist( train[[varName]], main=paste(TAG,varName), 100)
    #hist( train[[varName]], main=paste(TAG,varName), xlim=c(-1.5,2.5), 100)
    auc <- calcAUC( train[[varName]], train_actuals ) 
    plot.title <- paste(TAG,varName, "AUC:",as.character(auc))
    plotROC( train[[varName]], train_actuals, plot.title )
}

