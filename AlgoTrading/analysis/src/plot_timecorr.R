# plots correlation of time point (e.g. t51, t52...) with the buy/sell flag (1/0)
# --- configurable constants

PLOTFILE <- "plot_timecorr.pdf"

load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
dat.all <- probe
#load(file="/home/chefele/AlgoTrading/data/training.Rsave")
#dat.all <- training

pre.tperiods  <- 1:50
post.tperiods <- 51:100
all.tperiods  <- 1:100
event.tperiod <- 49
nearevent.tperiods <- 40:59

# --- internal constants 

mkNames   <- function(ask.or.bid, periods) { paste(ask.or.bid, as.character(periods),sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
all.bids  <- mkNames("bid", all.tperiods)
all.asks  <- mkNames("ask", all.tperiods)

security_ids <- sort(unique(dat.all$security_id))
initiators   <- sort(unique(dat.all$initiator))

# --- plotting functions

# Create plots of bids, asks correlations to initiator flag 
plotTimeCors <- function(in.dat, in.tag) { 

    asks      <-  cbind(in.dat[all.asks]) - cbind(in.dat$ask50)  # (instances) x (100 timeperiods )
    bids      <-  cbind(in.dat[all.bids]) - cbind(in.dat$bid50) 
    initiator <-  (in.dat$initiator=="B" ) * 1 
    asks.cors <-  cor(asks,initiator)
    bids.cors <-  cor(bids,initiator)
    #plot(asks.cors, main=paste(in.tag, "Asks"), xlab="Event Time", ylab="Corr with initiator")
    #plot(bids.cors, main=paste(in.tag, "Bids"), xlab="Event Time", ylab="Corr with initiator")
    plot(all.tperiods,  asks.cors[all.tperiods],  main=paste(in.tag, "Asks"), xlab="Event Time", ylab="Corr with initiator")
    plot(all.tperiods,  bids.cors[all.tperiods],  main=paste(in.tag, "Bids"), xlab="Event Time", ylab="Corr with initiator")
    plot(post.tperiods, asks.cors[post.tperiods], main=paste(in.tag, "Asks"), xlab="Event Time", ylab="Corr with initiator")
    plot(post.tperiods, bids.cors[post.tperiods], main=paste(in.tag, "Bids"), xlab="Event Time", ylab="Corr with initiator")
}


# --- main()

print("Now plotting correlation matrix for each security")
pdf(file=PLOTFILE)
par(mfrow=c(2,2)) # 2x2 matrix of plots 

#first do processing on ALL data
print("Subsetting data")
dat <-  dat.all
tag <-  paste("security_id: ALL")
print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
plotTimeCors(dat, tag)

# now do processing on each stock individually
for(security_id in security_ids) {
    security_id.mask <- dat.all$security_id == security_id
    dat <-  dat.all[ security_id.mask ,] 
    tag <-  paste("security_id:", security_id)
    print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
    plotTimeCors(dat, tag)
}


# TODO / Future work: 
# plot for t51-t100, x= %tradeSize, y=avg of asks/vwap, avg of bids/vwap, avg of midpts/vwap, avg of spreads/vwap
# plot mean t1-50 / mean t51-100 vs normalized trade size

