
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
train <- read.csv("~/Ford/blendall/fordTrain.assembled.features.csv")
train.samp <- train[ sample(1:nrow(train),10000) , ] 

pdf(file="variableROCs.pdf")

for( var.name in names(train) ) {
    plotROC(train[[var.name]], train$IsAlert, var.name)
    print(var.name)
}



