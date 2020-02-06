
library(caTools)

train <- read.csv("~/Ford/download/fordTrain.csv")

# Fix concave region in V11 ROC
THRESH_HIGH <- 0.6  # define percentile region for the fix 
THRESH_LOW  <- 0.3 
data <- train$V11
data.pct <- ecdf(data)(data) # use perentiles 
V11.fixed <- data.pct
fix.mask <- (data.pct>THRESH_LOW ) & (data.pct<THRESH_HIGH)
V11.fixed[fix.mask] <- THRESH_HIGH + THRESH_LOW - V11.fixed[fix.mask]

df.fixes <- data.frame( V11.fixed )
write.csv(df.fixes, file="fix.V11.train.csv", row.names=FALSE,quote=FALSE)


# -----------------------------------------------------------------------------

df.comparison <- data.frame(IsAlert=train$IsAlert, V11=train$V11, fixedV11=V11.fixed )
df.comparison.samp <-df.comparison[  sample(1:nrow(df.comparison),10000) , ] 
pdf(file="fix.V11.pdf")
aucs <- colAUC(df.comparison.samp, df.comparison.samp$IsAlert, plotROC=TRUE)
print(aucs)

# -----------------------------------------------------------------------------

test  <- read.csv("~/Ford/download/fordTest.csv")

# Fix concave region in V11 ROC
THRESH_HIGH <- 0.6  # define percentile region for the fix 
THRESH_LOW  <- 0.3 
data <- test$V11
data.pct <- ecdf(data)(data) # use perentiles 
V11.fixed <- data.pct
fix.mask <- (data.pct>THRESH_LOW ) & (data.pct<THRESH_HIGH)
V11.fixed[fix.mask] <- THRESH_HIGH + THRESH_LOW - V11.fixed[fix.mask]

df.fixes <- data.frame( V11.fixed )
write.csv(df.fixes, file="fix.V11.test.csv",row.names=FALSE,quote=FALSE)


