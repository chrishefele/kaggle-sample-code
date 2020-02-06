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

#pdf("plot_roc_hist.pdf")
#par(mfrow=c(2,2))   # (Rows,Cols) layout of multiple plots per page 

for(max_dsfs in c(1:12)) {
    for(varName in names(train_analog)) {
        t_analog  <- train_analog[[varName]]   # TODO SUBSET
        t_actuals <- train_actuals             # TODO SUBSET

        mask      <- train_analog$max_int_ClaimDSFS == max_dsfs
        t_analog  <- t_analog[ mask]
        t_actuals <- t_actuals[mask]

        auc <- calcAUC( t_analog, t_actuals )
        auc_char <- as.character(auc)
        plot.title <- paste(varName, "maxdsfs:", as.character(max_dsfs), "AUC:",auc_char, "greptag\n")
        cat(plot.title)
        # plotROC( train_analog[[varName]], train_actuals, plot.title ) 
        # hist( train_analog[[varName]] , main=paste(varName, "Histogram"))
    }
}


