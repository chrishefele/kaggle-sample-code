
library(ROCR)   # used to calcualate AUC
train <- read.csv("../download/fordTrain.csv")
TrialIDs <- unique(train$TrialID)
AUCs <- c()

# define function to calc AUC on a subset of trial IDs, using 1 variable as predictor
calc.trials.AUC <- function(some.data, trials.ids, predictor.var.name) {
	trials.data <- some.data[ some.data$TrialID %in% trials.ids , ] 
    predictions <- trials.data[[predictor.var.name]]
    labels      <- trials.data[["IsAlert"]]
    if(max(labels)==min(labels)) return(0.5) # default if IsAlert doesn't change
    pred.tmp    <- prediction(predictions, labels) # ROCR function
    trials.AUC  <- performance(pred.tmp, "auc")@y.values[[1]] 
    return(trials.AUC) 
}

for(trial.id in TrialIDs) {
    AUCs <- c(AUCs, calc.trials.AUC(train, c(trial.id),"V11"))
    print(trial.id)
}

pdf(file="V11_trial_AUCs.pdf") 
hist(AUCs, 50)
plot(sort(AUCs))
print(mean(AUCs))
print(sd(AUCs))
