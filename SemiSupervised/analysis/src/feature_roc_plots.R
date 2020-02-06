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

# plot histograms of 100 feature variables 

DATA_DIR <- "/home/chefele/SemiSupervised/data/data/"
TRAIN_BINARY  <- paste(DATA_DIR,"bsvd_features_train.csv",sep="")
TRAIN_ANALOG  <- paste(DATA_DIR,"train_analog.csv",sep="")
TRAIN_ACTUALS <- "/home/chefele/SemiSupervised/download/competition_data/public_train.labels.dat"

train_binary <- read.csv(TRAIN_BINARY,header=FALSE)
train_analog <- read.csv(TRAIN_ANALOG,header=FALSE)
train_actuals_df<- read.csv(TRAIN_ACTUALS,header=FALSE)
train_actuals<- train_actuals_df$V1

pdf("feature_roc_plots.pdf")
par(mfrow=c(2,2))   # (Rows,Cols) layout of multiple plots per page 

for(varName in names(train_binary)) {
    print(varName)
    auc <- calcAUC( train_binary[[varName]], train_actuals ) 
    plot.title <- paste("Binary:",varName, "AUC:",as.character(auc))
    plotROC( train_binary[[varName]], train_actuals, plot.title )
}

for(varName in names(train_analog)) {
    print(varName)
    auc <- calcAUC( train_analog[[varName]], train_actuals ) 
    plot.title <- paste("Analog:",varName, "AUC:",as.character(auc))
    plotROC( train_analog[[varName]], train_actuals, plot.title ) 
}


