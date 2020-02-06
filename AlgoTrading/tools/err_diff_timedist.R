# Calculate the differences in the error distribution across time of two sets of probe predictions
# invoke with:  cat err_timedist.R | R --vanilla --args <PREDS_FILE_1> <PREDS_FILE_2>
# This is useful to show if it's better to use a different predictor around the market open 

# --- configurable constants

PREDS_FILE_1 <- commandArgs(trailingOnly=TRUE)[1]  # must be probe file predictions
PREDS_FILE_2 <- commandArgs(trailingOnly=TRUE)[2]  # must be probe file predictions
PROBE_FILE   <- "/home/chefele/AlgoTrading/data/probe.Rsave"
PLOT_FILE    <- "err_diff_timedist.pdf"

# --- internal constants 

pre.tperiods  <- 1:50
post.tperiods <- 51:100

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

# --- get the data

load(file=PROBE_FILE)
preds1 <- read.csv(PREDS_FILE_1)
preds2 <- read.csv(PREDS_FILE_2)

# --- evaluate RMSE
getPrices <- function(df1)      { as.matrix(cbind(df1[post.bidasks])) }
getSqErrs <- function(df1,df2)  { (getPrices(df1) - getPrices(df2))^2 } # returns error^2 matrix
getRMSE   <- function(df1)      { sqrt(mean(getSqErrs(df1,probe)))    }

print( paste("RMSE of:", PREDS_FILE_1,"=", as.character(getRMSE(preds1))))
print( paste("RMSE of:", PREDS_FILE_2,"=", as.character(getRMSE(preds2))))

# --- calculate the time distribution of errors

parseHM  <- function(timeString) { strptime(timeString, format="%H:%M") }
hm       <- parseHM(probe$time49)         # hm is in seconds, truncated to hour & minute
hm.bin   <- as.numeric(hm - min(hm)) + 1  # make times relative to the start of the trading day

preds1.mses <- rowMeans( getSqErrs(preds1, probe) )  
preds2.mses <- rowMeans( getSqErrs(preds2, probe) )  
preds1.sqerrs.binned <- tapply(preds1.mses, hm.bin, sum)
preds2.sqerrs.binned <- tapply(preds2.mses, hm.bin, sum)
preds1.counts.binned <- tapply( rep.int(1,length(hm.bin)), hm.bin, sum)
preds2.counts.binned <- tapply( rep.int(1,length(hm.bin)), hm.bin, sum)

diff.sqerrs.binned <- preds1.sqerrs.binned - preds2.sqerrs.binned 

#avg errors 
print(preds1.counts.binned)
print(preds2.counts.binned)
print(preds1.sqerrs.binned / preds1.counts.binned)
print(preds2.sqerrs.binned / preds2.counts.binned)

print(diff.sqerrs.binned / sum(  diff.sqerrs.binned))
print(diff.sqerrs.binned / sum(preds1.sqerrs.binned))
print(diff.sqerrs.binned / sum(preds2.sqerrs.binned))

print(cumsum(diff.sqerrs.binned) / sum(  diff.sqerrs.binned))
print(cumsum(diff.sqerrs.binned) / sum(preds1.sqerrs.binned))
print(cumsum(diff.sqerrs.binned) / sum(preds2.sqerrs.binned))

pdf(file=PLOT_FILE)
PT <- "b" # p=pts, l=lines, b=both
LG <- "x" # log scale axis, or NULL

plot(diff.sqerrs.binned / sum(  diff.sqerrs.binned), type=PT, log=LG, main="SqErr Diff as Frac of Tot Diff SqErr")
plot(cumsum(diff.sqerrs.binned)/sum(diff.sqerrs.binned), type=PT, log=LG, 
        main="Cumulative SqErr Diff vs Time as Frac of Tot SqErr Diff")
#plot(diff.sqerrs.binned / sum(preds1.sqerrs.binned), type=PT, log=LG, main="SqErr Diff as Frac of Tot P1   SqErr")
#plot(diff.sqerrs.binned / sum(preds2.sqerrs.binned), type=PT, log=LG, main="SqErr Diff as Frac of Tot P2   SqErr")

plot(preds1.sqerrs.binned / preds1.counts.binned, type=PT, log=LG, main="P1 Mean SqErr vs Time  ")
plot(preds2.sqerrs.binned / preds1.counts.binned, type=PT, log=LG, main="P2 Mean SqErr vs Time  ")


