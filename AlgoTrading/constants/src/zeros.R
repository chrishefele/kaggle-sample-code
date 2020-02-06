# create a submission of all zeros (or almost 0)

ZERO <- 0.000001
USE_PROBE <- FALSE # false to create testing file, true to create probe file

if(USE_PROBE) {
    PREDS_OUT <- "zeros.probe.csv"
    load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
    in.dat <- probe
} else {
    PREDS_OUT<- "zeros.testing.csv"
    load(file="/home/chefele/AlgoTrading/data/testing.Rsave")
    in.dat <- testing
}

pre.tperiods  <- 1:50
post.tperiods <- 51:100

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

# ------------------- make predictions 

preds <- data.frame(row_id=in.dat$row_id)
preds[,post.bidasks] <- ZERO # create new columns in right sequence

if(USE_PROBE) {
    scoreRMSE <- function(preds, actuals, eval.cols) {
        preds.matrix   <- as.matrix(cbind(preds[, eval.cols]))
        actuals.matrix <- as.matrix(cbind(actuals[, eval.cols]))
        rmse <- sqrt(mean( (preds.matrix-actuals.matrix)^2 ))
        return(rmse)
    } 
    preds.matrix   <- as.matrix(cbind(preds[post.bidasks]))
    actuals.matrix <- as.matrix(cbind(probe[post.bidasks]))
    rmse <- sqrt(mean( (preds.matrix-actuals.matrix)^2 ))
    print(rmse)
    print( scoreRMSE(preds, probe, post.bidasks) ) 
}

write.csv(preds, file=PREDS_OUT, quote=FALSE, row.names=FALSE, col.names=TRUE)
print(paste("write to:", PREDS_OUT))

