# regression-dynamics-postprocessing.R  
# by Chris Hefele December, 2011
# Collects files created by regression.R in 'dynamic' mode & creates a submission file
# for the Algorithmic Trading Challenge on Kaggle.com 

# --- configurable constants

DATA_DIR         <- "/home/chefele/AlgoTrading/data/"
DYNAMIC_DIR      <- "dynamics.cache/"  # directory with files for individual time predictions 
SUBMISSION_FILE  <- "regression.dynamics.testing.csv"
PROBE_OUT        <- "regression.dynamics.probe.csv"
PREDICTION_TIMES <- 51:100

bid.names   <- paste("bid", as.character(PREDICTION_TIMES),sep="")
ask.names   <- paste("ask", as.character(PREDICTION_TIMES),sep="")
bidask.names<- as.vector(rbind(bid.names,ask.names))

# --- load & assemble data from seperate files
load(paste(DATA_DIR, "probe.Rsave", sep="")) 
preds.probe   <- read.csv(paste(DYNAMIC_DIR,"probe.row_id.csv",  sep=""))
preds.testing <- read.csv(paste(DYNAMIC_DIR,"testing.row_id.csv",sep=""))

for(i in PREDICTION_TIMES) { 
    fname.probe   <- paste(DYNAMIC_DIR,"probe.t",   as.character(i),".csv",sep="")
    fname.testing <- paste(DYNAMIC_DIR,"testing.t", as.character(i),".csv",sep="")
    print(paste("Reading:", fname.probe, "&", fname.testing))
    preds.probe   <- cbind( preds.probe,   read.csv(fname.probe)   )
    preds.testing <- cbind( preds.testing, read.csv(fname.testing) )
}

# --- calculate RMSE
errs <- as.matrix(preds.probe[,bidask.names] - probe[,bidask.names])
rmse <- sqrt(mean(errs*errs))
print(paste("RMSE of probe predictions:", as.character(rmse)))

# --- write probe file
print(paste("Writing probe file to:", PROBE_OUT))
write.csv(preds.probe, file=PROBE_OUT, quote=FALSE, row.names=FALSE, col.names=TRUE)

# --- write prediction file
print(paste("Writing submission file to:", SUBMISSION_FILE))
write.csv(preds.testing, file=SUBMISSION_FILE, quote=FALSE, row.names=FALSE, col.names=TRUE)

print("Done.")

