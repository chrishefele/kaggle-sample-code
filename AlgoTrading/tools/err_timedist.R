# Calculate error distribution across time of a given probe file
# invoke with:  cat err_timedist.R | R --vanilla --args <INFILE> 

INFILE   <- commandArgs(trailingOnly=TRUE)[1]
PLOTFILE <- "err_timedist.pdf"

load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- probe 

pre.tperiods  <- 1:50
post.tperiods <- 51:100

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

# ------------------- get predictions 

preds <- read.csv(INFILE)

# ------------------- evaluate RMSE

preds.matrix   <- as.matrix(cbind(preds[post.bidasks]))
actuals.matrix <- as.matrix(cbind(in.dat[post.bidasks]))
err.matrix <- preds.matrix - actuals.matrix

rmse <- sqrt(mean(err.matrix^2))
print(paste("Overall RMSE:", as.character(rmse)))

# now show how the error is distributed over time (H:M=hour:minute)

parseHM  <- function(timeString) { strptime(timeString, format="%H:%M") }
hm <- parseHM(in.dat$time49)
hm.min <- min(hm)
hm.by.row <- hm - hm.min

mse.by.row <- rowMeans( err.matrix^2 ) 
mse.by.hm <- tapply(mse.by.row, hm.by.row, sum)
 
#print(sort(mse.by.hm, decreasing=TRUE))
#print(sort(mse.by.hm, decreasing=TRUE) / sum(mse.by.hm) ) 
#print(cumsum(sort(mse.by.hm, decreasing=TRUE)) / sum(mse.by.hm) )

print(mse.by.hm)
print(mse.by.hm / sum(mse.by.hm)) 
print(cumsum(mse.by.hm) / sum(mse.by.hm) )

pdf(PLOTFILE)
plot(mse.by.hm / sum(mse.by.hm), main="SqErr vs Time") 
plot(cumsum(mse.by.hm) / sum(mse.by.hm) , main="Cumulative SqErr vs Time")

