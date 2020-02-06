
sub <- read.csv("ford.submission.logistic.lambdapath.csv")
df <- data.frame(  TrialID=sub$TrialID, ObsNum=sub$ObsNum )

for(var.name in names(sub)) {
    df$Prediction <- sub[[var.name]] 
    new.filename <- paste("ford.submission.logistic.lambdapath.",var.name,".csv",sep="") 
    write.csv(df, file=new.filename, row.names=FALSE, quote=FALSE)
}


