
library(caTools)

train <- read.csv("~/Ford/download/fordTrain.csv")
train.samp <- train[ sample(1:nrow(train),10000) , ] 

# pdf(file="thresholdROCs.pdf")

for( var.name in names(train) ) {

x <- train.samp[[var.name]]
percentiles <- ecdf(x)(x)
lt10 <- (percentiles<0.1)*1
gt90 <- (percentiles>0.9)*1
df <- data.frame(lt10, gt90)
df[[var.name]] <- x
aucs <- colAUC(df, train.samp$IsAlert, plotROC=TRUE)
print(var.name)
print(aucs)

}



