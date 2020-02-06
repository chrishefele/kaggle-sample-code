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


DATA_DIR <- "./"
TRAIN_ANALOG  <- paste(DATA_DIR,"Y1_features.csv",sep="")
TRAIN_ACTUALS <- "Y1_answers.csv"

train_analog     <- read.csv(TRAIN_ANALOG)
train_actuals_df <- read.csv(TRAIN_ACTUALS)
train_actuals    <- (train_actuals_df$DaysInHospital > 0)*1

pdf("plot_roc_hist.pdf")
par(mfrow=c(2,2))   # (Rows,Cols) layout of multiple plots per page 

for(varName in names(train_analog)) {
    auc <- calcAUC( train_analog[[varName]], train_actuals ) 
    auc_char <- as.character(auc)
    plot.title <- paste(varName, "AUC:",auc_char)
    plotROC( train_analog[[varName]], train_actuals, plot.title ) 
    hist( train_analog[[varName]] , main=paste(varName, "Histogram"))
    cat(auc_char)
    cat(" ")
    cat(varName)
    cat(" grep")
    cat("tag")
    cat("\n")
}


