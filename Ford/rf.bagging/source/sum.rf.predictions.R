# program to sum the all the individual predictions in rf.bagging/predictions directory
# to form the final result for submission

PREDICTIONS_DIRECTORY  <- "/home/chefele/Ford/rf.bagging/predictions"
MERGED_SUBMISSION_FILE <- "ford.submission.rf.bagging.result.csv"

sum.of.preds <- 0.0
for( fname in dir(path=PREDICTIONS_DIRECTORY,full.names=TRUE) )  {
   print(fname)
   preds <- read.csv(fname)
   sum.of.preds <- sum.of.preds + preds$Prediction
}
out.data <- data.frame( TrialID=preds$TrialID, 
                        ObsNum=preds$ObsNum, 
                        Prediction=(sum.of.preds/max(sum.of.preds)) 
            )
write.csv(out.data, file=MERGED_SUBMISSION_FILE, quote=FALSE, row.names=FALSE)

num.files <- length(dir(path=PREDICTIONS_DIRECTORY,full.names=TRUE))
print( paste("Summed ",as.character(num.files)," files",sep="") )
print( paste("Wrote results to file: ",MERGED_SUBMISSION_FILE,sep="") ) 
print( paste("Sum statistics: ",  
             "max: ", as.character(max(sum.of.preds)),
             "min: ", as.character(min(sum.of.preds))
            )
     )


