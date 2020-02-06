
library(caTools)

train <- read.csv("~/Ford/download/fordTrain.csv")
train.samp <- train[ sample(1:nrow(train),10000) , ] 

pdf(file="thresh.median.ROCs.pdf")

for( var.name in names(train) ) {

x <- train.samp[[var.name]]
percentiles <- ecdf(x)(x)
above.median <- (percentiles>0.9)*1
df <- data.frame( above.median ) 
df[[var.name]] <- x
aucs <- colAUC(df, train.samp$IsAlert, plotROC=TRUE)
print(var.name)
print(aucs)

}

