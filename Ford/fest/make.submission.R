
preds <- as.vector( scan("pred.test.fest.c3t100.rf.out") )

test <- read.csv("/home/chefele/Ford/download/fordTest.csv")

submission <- data.frame( TrialID=test$TrialID, ObsNum=test$ObsNum, Prediction=preds )

write.csv(submission, file="ford.submission.fest.c3t100.rf.csv", quote=FALSE, row.names=FALSE)





