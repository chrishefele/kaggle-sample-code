
# read in "probe" holdout set, which is the last 50K lines of training.csv
load("/home/chefele/AlgoTrading/data/probe.Rsave")

bid.names <- paste("bid",as.character(51:100),sep="")
ask.names <- paste("ask",as.character(51:100),sep="")
bidask.names <- as.vector(rbind(bid.names, ask.names))

# naive predictor #1 -- predict bid/ask51...100 = bid/ask 50
preds1 <- data.frame(probe[,bidask.names])
preds1[,bid.names] <- probe[,"bid50"]
preds1[,ask.names] <- probe[,"ask50"]

# naive predictor #2 -- predict bid/ask51...100 = bid/ask 45
preds2 <- data.frame(probe[,bidask.names])
preds2[,bid.names] <- probe[,"bid50"]
preds2[,ask.names] <- probe[,"ask49"]

errs1   <- cbind(probe[,bidask.names]) - cbind(preds1[,bidask.names])
errs2   <- cbind(probe[,bidask.names]) - cbind(preds2[,bidask.names])
sqerrs1 <- rowMeans(errs1*errs1)
sqerrs2 <- rowMeans(errs2*errs2)

rmse.diffs <- c()
SAMP_SIZE <- 50000 * 0.70 # 70% for private, 30% for public leaderboard
for(i in 1:1000) {
    rows.sample <- sample(1:50000, SAMP_SIZE)
    rmse1.sample <-  sqrt( sum(sqerrs1[rows.sample]) / SAMP_SIZE) 
    rmse2.sample <-  sqrt( sum(sqerrs2[rows.sample]) / SAMP_SIZE)
    rmse.diff    <- rmse1.sample - rmse2.sample
    rmse.diffs <- c(rmse.diffs, rmse.diff)
    print(i)
}
print(sd(rmse.diffs))
print(mean(rmse.diffs))
print(sd(rmse.diffs)/mean(rmse.diffs))
pdf(file="lead-swap.pdf")
hist(rmse.diffs, 100, main="Histogram of gap between 2 naive predictors")


