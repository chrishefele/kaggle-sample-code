
library(caTools)
LOOPS <- 1000
auc.gaps <- c()
train <- read.csv("../download/fordTrain.csv")
TrialIDs <- unique(train$TrialID)

for(loop in 1:LOOPS) {

    sample.TrialIDs.100 <- sample( TrialIDs,100 )  # Pick 100 trials for simulated test set...
    sample.TrialIDs.30  <- sample(  sample.TrialIDs.100, 30 )  # Of those, use 30 IDs for the leaderboard test AUC
    sample.TrialIDs.70  <- setdiff( sample.TrialIDs.100, sample.TrialIDs.30) # Use remaining IDs for prize test AUC 

    train.sample.30 <- train[ train$TrialID %in% sample.TrialIDs.30 , ]
    train.sample.70 <- train[ train$TrialID %in% sample.TrialIDs.70 , ]

    auc.train.sample.30 <- colAUC( train.sample.30$V11, train.sample.30$IsAlert, plotROC=FALSE )
    auc.train.sample.70 <- colAUC( train.sample.70$V11, train.sample.70$IsAlert, plotROC=FALSE )

    auc.gap <- auc.train.sample.30[1,1] -  auc.train.sample.70[1,1]  # gap between leaderboard & "actual"/prize AUC
    auc.gaps <- c(auc.gaps, auc.gap)
    print(loop)

}

pdf(file="hist_auc_leaderboard.pdf") 
hist(auc.gaps, 50)
print(mean(auc.gaps))
print(sd(auc.gaps))
