library(glmnet)
library(ROCR) 

TEST_SOLUTION_FILE <- "/home/chefele/Ford/download/fordTestSolution.csv" 
SUBMISSION_FILE    <- "8317.csv"

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

# ---------------------

submission <- read.csv(SUBMISSION_FILE)

x1 <- as.matrix( ecdf(submission$Prediction)(submission$Prediction) -0.5) *2
x2 <- as.matrix( ecdf(test.soln$TrialAUC)(test.soln$TrialAUC)       -0.5) *2 

X <- cbind(x1, x1^2, x1^3, x2, x2^2, x2^3)
Y <- as.matrix(test.soln$Actuals)

fit <- cv.glmnet(X, Y, type.measure="auc", family="binomial") 
coef(fit)
print(fit)

blended.prediction <- predict( fit, newx=X, type="response")

print( calcAUC(test.soln$TrialAUC,    test.soln$Actuals) ) 
print( calcAUC(submission$Prediction, test.soln$Actuals) ) 
print( calcAUC(blended.prediction,    test.soln$Actuals) ) 


