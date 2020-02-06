
library(caTools)
LOOPS <- 1000
aucs <- c()
train <- read.csv("../download/fordTrain.csv")
TrialIDs <- unique(train$TrialID)

for(loop in 1:LOOPS) {
    # randomly select 30 complete trials of data & then calculate AUC of V11
    train.sample <- train[ train$TrialID %in% sample(TrialIDs,30), ]
    auc.train.sample <- colAUC( train.sample$V11, train.sample$IsAlert, plotROC=FALSE )
    aucs <- c(aucs, auc.train.sample[1,1])
    print(loop)
}

pdf(file="hist_auc_sample.pdf") 
hist(aucs, 50)
print(mean(aucs))
print(sd(aucs))
