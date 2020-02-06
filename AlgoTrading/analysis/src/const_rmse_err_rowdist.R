# Calculate error distribution across time assuming a constant predictor for bid/ask

#load(file="/home/chefele/AlgoTrading/data/training.Rsave") 
#in.dat <- training
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- probe # probe or training

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
preds[,post.bidasks] <- 0  # create new columns in right sequence

# optimum RMSE using a constant bid/ask is just the average of bids/asks
USE_OPTIMUM <- FALSE
if(USE_OPTIMUM) {
    # gets RMSE of 0.7497644 on probe, 0.7918093 on training 
    preds[post.asks] <- rowMeans( as.matrix(cbind(in.dat[post.asks])))
    preds[post.bids] <- rowMeans( as.matrix(cbind(in.dat[post.bids])))
} else { # use naieve predictor
    # gets RMSE of 1.269548 on probe,  1.338763 on training 
    preds[post.asks] <- in.dat["ask50"] 
    preds[post.bids] <- in.dat["bid50"]
}

# ------------------- evaluate RMSE

preds.matrix   <- as.matrix(cbind(preds[post.bidasks]))
actuals.matrix <- as.matrix(cbind(in.dat[post.bidasks]))
err.matrix <- preds.matrix - actuals.matrix
log.err.matrix <- log(preds.matrix) - log(actuals.matrix)

rmse <- sqrt(mean(err.matrix^2))
print(rmse)

# now show how the error is distributed over stocks & rows

se.rowsums           <- rowSums( err.matrix^2 ) 
sqerr.by.row_id      <- tapply(se.rowsums, in.dat$row_id,      sum)

log.se.rowsums           <- rowSums( log.err.matrix^2 ) 
log.sqerr.by.row_id      <- tapply(log.se.rowsums, in.dat$row_id,      sum)

# want log/log plot of error vs rank

pdf("const_rmse_err_rowdist.pdf")

errs.sorted <- sort(sqerr.by.row_id, decreasing=TRUE) / sum(sqerr.by.row_id) 
print(cumsum(errs.sorted))
plot( cumsum(errs.sorted), type="l", log="x", 
        ylab="Cumulative (P1-P2)^2 [solid line] ...or... (log(P1)-Log(P2))^2 [dashed line]", 
        xlab="Number of Rows (Sorted by error contribution)", 
        main="Cumulative Squared (Log) Errors using the Naive Predictor \non the Last 50K Lines of Training.csv")

log.errs.sorted <- sort(log.sqerr.by.row_id, decreasing=TRUE) / sum(log.sqerr.by.row_id) 
print(cumsum(log.errs.sorted))
lines( cumsum(log.errs.sorted), lty=3)

