
load(             "/home/chefele/AlgoTrading/data/probe.Rsave")
preds <- read.csv("/home/chefele/AlgoTrading/regression/src/regression.probe.csv")

bid.names <- paste("bid",as.character(51:100),sep="")
ask.names <- paste("ask",as.character(51:100),sep="")
bidask.names <- as.vector(rbind(bid.names, ask.names))

errs   <- cbind(probe[,bidask.names]) - cbind(preds[,bidask.names])

#mean.price <- cbind(probe[,bidask.names]) 
#errs   <- errs / probe$trade_vwap * mean.price

sqerr.rowsums <- rowMeans(errs*errs)

tot.sqerr <- sum(sqerr.rowsums)
rmse.diffs <- c()
for(i in 1:1000) {
    samp.sqerr <- sum(sample(sqerr.rowsums, 35000))
    rmse.70 <- sqrt(samp.sqerr/35000)
    rmse.30 <- sqrt( (tot.sqerr - samp.sqerr)/15000) 
    rmse.diff <- rmse.70 - rmse.30
    rmse.diffs <- c(rmse.diffs, rmse.diff)
    print(i)
}
print(sd(rmse.diffs))
print(mean(rmse.diffs))
print(sd(rmse.diffs)/mean(rmse.diffs))
pdf(file="leaderboard.std.pdf")
hist(rmse.diffs, 100, main="Histogram of difference between private & public eaderboard scores")


