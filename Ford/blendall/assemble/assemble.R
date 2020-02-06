# 

spikeTrialTest <- function(df) { (df$P2 > 12.5)*1 }  
# test for a spike trial, given dataframe; 12.5 threshold derived from graphs of P2; output is 1|0 vector

test<- read.csv("/home/chefele/Ford/download/fordTest.csv")
test.l1se.lags <- read.csv("/home/chefele/Ford/blendall/lambda.1se/pred.logistic.lags.test.csv")
test.l02.lags <- read.csv("/home/chefele/Ford/blendall/lambda.02/pred.logistic.lags.test.csv")
test.l1se.absdiffs <- read.csv("/home/chefele/Ford/blendall/lambda.1se/pred.logistic.absdiffs.test.csv")
test.l02.absdiffs <-read.csv("/home/chefele/Ford/blendall/lambda.02/pred.logistic.absdiffs.test.csv")
test.fp <- read.csv("/home/chefele/Ford/mkfeatures/fordTest.features.picked.csv")
test.spikemerge <- read.csv("/home/chefele/Ford/logistic.spikes/pred.logistic.absdiffs.test.spikemerge.csv")
test.fix.V11 <- read.csv("/home/chefele/Ford/fix.V11/fix.V11.test.csv")

test.fp$logmin.x.V11. <- NULL   # removed to reduce collinearity after V11.fixed variable added 

test.outdata <- 
    cbind(
        as.matrix(
            data.frame(
               TrialID = test$TrialID, 
               ObsNum = test$ObsNum, 
               IsAlert = test$IsAlert, 
               LR.lags.L1SE    =test.l1se.lags$X1, 
               LR.lags.L02     =test.l02.lags$X1, 
               LR.absdiffs.L1SE=test.l1se.absdiffs$X1, 
               LR.absdiffs.L02 =test.l02.absdiffs$X1, 
               # LR.absdiffs.spikemerge = test.spikemerge$X1,
               IsSpikeTrial = spikeTrialTest(test),            # REMOVE THIS???
               TrialFirst100 = sign(test$ObsNum - 100),
               V11.fixed = test.fix.V11$V11.fixed           # ADDED 
            )
        ), 
        as.matrix(test.fp)
    )
write.csv(test.outdata, file="fordTest.assembled.features.csv",quote=FALSE, row.names=FALSE)



train <- read.csv( "/home/chefele/Ford/download/fordTrain.csv")
train.l1se.lags <- read.csv( "/home/chefele/Ford/blendall/lambda.1se/pred.logistic.lags.train.csv")
train.l02.lags <- read.csv( "/home/chefele/Ford/blendall/lambda.02/pred.logistic.lags.train.csv" )
train.l1se.absdiffs <- read.csv( "/home/chefele/Ford/blendall/lambda.1se/pred.logistic.absdiffs.train.csv")
train.l02.absdiffs <- read.csv( "/home/chefele/Ford/blendall/lambda.02/pred.logistic.absdiffs.train.csv" )
train.fp <- read.csv( "/home/chefele/Ford/mkfeatures/fordTrain.features.picked.csv")
train.spikemerge <- read.csv("/home/chefele/Ford/logistic.spikes/pred.logistic.absdiffs.train.spikemerge.csv")
train.fix.V11 <- read.csv("/home/chefele/Ford/fix.V11/fix.V11.train.csv")

train.fp$logmin.x.V11. <- NULL   # removed to reduce collinearity after V11.fixed variable added 

train.outdata <- 
    cbind(
        as.matrix(
            data.frame(
               TrialID = train$TrialID, 
               ObsNum = train$ObsNum, 
               IsAlert = train$IsAlert, 
               LR.lags.L1SE    =train.l1se.lags$X1, 
               LR.lags.L02     =train.l02.lags$X1, 
               LR.absdiffs.L1SE=train.l1se.absdiffs$X1, 
               LR.absdiffs.L02 =train.l02.absdiffs$X1,
               # LR.absdiffs.spikemerge = train.spikemerge$X1,
               IsSpikeTrial = spikeTrialTest(train),            # REMOVE THIS ???
               TrialFirst100 = sign(train$ObsNum - 100),
               V11.fixed = train.fix.V11$V11.fixed              # ADDED 
            )
        ), 
        as.matrix(train.fp)
    )
write.csv(train.outdata, file="fordTrain.assembled.features.csv", quote=FALSE, row.names=FALSE)

