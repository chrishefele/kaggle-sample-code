
library(caTools)

THRESH_HIGH <- 0.6  # define percentile region for the fix 
THRESH_LOW  <- 0.3 


train <- read.csv("~/Ford/download/fordTrain.csv")
train.samp <- train[ sample(1:nrow(train),10000) , ] 

pdf(file="fixV11.pdf")

var.name <- "V11"
data <- train.samp[[var.name]]
data.pct <- ecdf(data)(data)
pct.thresholds <- (1:9)/10.0

fix.mask <- (data.pct>THRESH_LOW ) & (data.pct<THRESH_HIGH)
fixed <- data.pct
fixed[fix.mask] <- THRESH_HIGH + THRESH_LOW - fixed[fix.mask]

df <- data.frame( V11.original=data.pct, V11.fixed=fixed )
aucs <- colAUC(df, train.samp$IsAlert, plotROC=TRUE)
print(var.name)
print(aucs)

