library(ROCR) 

TEST_SOLUTION_FILE <- "/home/chefele/Ford/download/fordTestSolution.csv" 

calcAUC <- function(predictions, labels) {  # uses ROCR library
                performance(prediction(predictions,labels), "auc")@y.values[[1]] 
} 

test.soln  <- read.csv(TEST_SOLUTION_FILE)
test.soln$Actuals  <- test.soln$Prediction  # just rename it, to be clear 
test.soln$TrialAUC <- 0  # for all observations in individual trials, predict the AUC as in the loop below

for(current.trial in unique(test.soln$TrialID)) {
    trial.mask <- (test.soln$TrialID == current.trial)
    mock.prediction <- 0 * test.soln$Prediction # initialize to the right length 
    mock.prediction[ trial.mask] <- 1  # for this trial, predict all 1's 
    mock.prediction[!trial.mask] <- 0  # else predict 0 
    trial.auc <- calcAUC(mock.prediction, test.soln$Actuals)
    test.soln$TrialAUC[trial.mask] <- trial.auc 
    print( paste( as.character(current.trial), as.character(trial.auc) ))
}

print( calcAUC(test.soln$TrialAUC, test.soln$Actuals) ) 






