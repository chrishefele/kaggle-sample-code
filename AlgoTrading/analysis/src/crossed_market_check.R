# Check for crossed markets

load(file="/home/chefele/AlgoTrading/data/training.Rsave") 
in.dat <- training
#load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
#in.dat <- probe # probe or training

pre.tperiods  <- 1:50
post.tperiods <- 51:100
all.tperiods  <- 1:100

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
all.bids  <- mkNames("bid", all.tperiods)
all.asks  <- mkNames("ask", all.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

# ------------------- check for crossed markets (bid < ask)

asks <- as.matrix(cbind(in.dat[all.asks]))
bids <- as.matrix(cbind(in.dat[all.bids]))

normal  <- sum( asks >  bids ) 
locked  <- sum( asks == bids ) 
crossed <- sum( asks <  bids ) 

print(normal)
print(locked)
print(crossed)

