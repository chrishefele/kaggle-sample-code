# Program to calculate a histogram of the variations in the difference
# between the test & train set AUCs in the Ford "Stay Alert!" challenge
# It uses variable V11 as a simple predictor (which by itself has an AUC ~0.7),
# and randomly partititions the trials into test/train subsets

library(ROCR)   # used to calcualate AUC
LOOPS <- 1000
AUC.gaps <- c()
train <- read.csv("../download/fordTrain.csv")
TrialIDs <- unique(train$TrialID)

# Function to calculate AUC on a subset of trial IDs, using 1 variable as predictor
calc.trials.AUC <- function(some.data, trials.ids, predictor.var.name) {
	trials.data <- some.data[ some.data$TrialID %in% trials.ids , ] 
    predictions <- trials.data[[predictor.var.name]]
    labels      <- trials.data[["IsAlert"]]
    pred.tmp    <- prediction(predictions, labels) # ROCR function
    trials.AUC  <- performance(pred.tmp, "auc")@y.values[[1]] # ROCR function
    return(trials.AUC) 
}

for(loop in 1:LOOPS) {

    # Randomly partition the trials into the various subsets 
    testTrials.all          <- sample( TrialIDs, 100 )        
    testTrials.leaderboard  <- sample( testTrials.all, 30 )  
    testTrials.prize        <- setdiff( testTrials.all, testTrials.leaderboard) 
    trainTrials             <- setdiff( TrialIDs, testTrials.all)  

    AUC.gap <- calc.trials.AUC(train, testTrials.leaderboard,"V11") - 
               calc.trials.AUC(train, trainTrials     ,      "V11")
    AUC.gaps <- c(AUC.gaps, AUC.gap)
    print(loop)
}

pdf(file="Ford_test_vs_train_gap_histogram.pdf") 
hist(AUC.gaps, 50)
print(mean(AUC.gaps))
print(sd(AUC.gaps))
