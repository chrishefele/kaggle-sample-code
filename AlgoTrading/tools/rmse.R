# rmse.R 
# usage:   cat rmse.R | R --vanilla --args <PROBEFILE> 

INFILE   <- commandArgs(trailingOnly=TRUE)[1]
DATA_DIR <- "/home/chefele/AlgoTrading/data/"
PREDICTION_TIMES <- 51:100

bid.names   <- paste("bid", as.character(PREDICTION_TIMES),sep="")
ask.names   <- paste("ask", as.character(PREDICTION_TIMES),sep="")
bidask.names<- as.vector(rbind(bid.names,ask.names))

load(paste(DATA_DIR, "probe.Rsave", sep="")) 
print(paste("Reading:", INFILE))
preds.probe  <- read.csv(INFILE)

#print(bidask.names)
#print(names(probe))
#print(names(preds.probe))

errs <- as.matrix(preds.probe[,bidask.names] - probe[,bidask.names])
rmse <- sqrt(mean(errs*errs))
print(paste("RMSE of probe predictions:", as.character(rmse)))
print(paste("RMSE::", as.character(rmse),INFILE ))

