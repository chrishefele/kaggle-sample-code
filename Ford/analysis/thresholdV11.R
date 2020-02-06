
library(caTools)

train <- read.csv("~/Ford/download/fordTrain.csv")
train.samp <- train[ sample(1:nrow(train),10000) , ] 

# pdf(file="thresholdROCs.pdf")

var.name <- "V11"
data <- train.samp[[var.name]]
data.percentiles <- ecdf(data)(data)
pct.thresholds <- (1:9)/10.0

df <- data.frame(data.percentiles)
for(pct.thresh in pct.thresholds) {

thresh.label <- paste("thresh_",as.character(pct.thresh),sep="")
thresh.data <- (data.percentiles<pct.thresh)*1
df[[thresh.label]] <- thresh.data

}

aucs <- colAUC(df, train.samp$IsAlert, plotROC=TRUE)
print(var.name)
print(aucs)

