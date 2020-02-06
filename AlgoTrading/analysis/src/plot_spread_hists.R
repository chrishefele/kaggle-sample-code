# Plot spread histograms

#load(file="/home/chefele/AlgoTrading/data/training.Rsave") 
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- probe # probe or training

pre.tperiods  <- 1:50
post.tperiods <- 51:100
all.tperiods  <- 1:100
event.tperiod <- 49

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
all.bids  <- mkNames("bid", all.tperiods)
all.asks  <- mkNames("ask", all.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

# ------------------- 

parseHMS <- function(timeString) { strptime(timeString, format="%H:%M:%OS") }

# ------------------- 

pdf(file="plot_spread_hists.pdf")
for(security_id in sort(unique(probe$security_id))) {
    print(security_id)
    asks <- as.matrix(cbind(in.dat[security_id == probe$security_id ,all.asks]))
    bids <- as.matrix(cbind(in.dat[security_id == probe$security_id ,all.bids]))
    spreads <- asks - bids
    hist(log10(spreads), 100, main=paste("security_id:", as.character(security_id)) )
}

