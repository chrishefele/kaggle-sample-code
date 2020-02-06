
library(ROCR)   # used to calcualate AUC
LOOPS <- 1000
AUC.gaps <- c()
train <- read.csv("../download/fordTrain.csv")
TrialIDs <- unique(train$TrialID)

# define function to calc AUC on a subset of trial IDs, using 1 variable as predictor
calc.trials.AUC <- function(some.data, trials.ids, predictor.var.name) {
	trials.data <- some.data[ some.data$TrialID %in% trials.ids , ] 
    predictions <- trials.data[[predictor.var.name]]
    labels      <- trials.data[["IsAlert"]]
    pred.tmp    <- prediction(predictions, labels) # ROCR function
    trials.AUC  <- performance(pred.tmp, "auc")@y.values[[1]] 
    return(trials.AUC) 
}

for(loop in 1:LOOPS) {

    testTrials.all          <- sample( TrialIDs, 100 )        
    testTrials.leaderboard  <- sample( testTrials.all, 30 )  
    testTrials.prize        <- setdiff( testTrials.all, testTrials.leaderboard) 
    trainTrials             <- setdiff( TrialIDs, testTrials.all)  

    AUC.gap <- calc.trials.AUC(train, testTrials.leaderboard,"V11") - 
               calc.trials.AUC(train, trainTrials     ,      "V11")
    AUC.gaps <- c(AUC.gaps, AUC.gap)
    print(loop)
}

pdf(file="hist_auc_leaderboard_ver2.pdf") 
hist(AUC.gaps, 50)
print(mean(AUC.gaps))
print(sd(AUC.gaps))
