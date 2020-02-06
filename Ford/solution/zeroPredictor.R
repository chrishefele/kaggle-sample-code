library(ROCR) 

TEST_SOLUTION_FILE <- "/home/chefele/Ford/download/fordTestSolution.csv" 
# SUBMISSION_FILE    <- "/home/chefele/Ford/blendall/ford.submission.logistic.fixV11substitute.csv"
SUBMISSION_FILE    <- "8317.csv"

ZERO_TRIALS <- c(3,4,8,9,19,20,21,22,77)

calcAUC <- function(predictions, labels) {  # uses ROCR library
                performance(prediction(predictions,labels), "auc")@y.values[[1]] 
} 

test.soln  <- read.csv(TEST_SOLUTION_FILE)

submission <- read.csv(SUBMISSION_FILE)
# submission$Prediction <- submission$X1

print( calcAUC( submission$Prediction, test.soln$Prediction ) ) 

for(zero.trial in ZERO_TRIALS) {
    submission$Prediction[ submission$TrialID == zero.trial ] <- 0 
}

print( calcAUC(submission$Prediction, test.soln$Prediction) ) 






