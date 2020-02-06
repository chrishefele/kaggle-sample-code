library("ROCR")

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

labels       <- c( rep(1,50), rep(0,50) )
prediction   <- rep( c(100:1))
print(calcAUC(prediction, labels))

