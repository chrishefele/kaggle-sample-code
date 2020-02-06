# --- configurable constants

PLOTFILE <- "plot_price_discreteness.pdf"

#load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
#dat.all <- probe
load(file="/home/chefele/AlgoTrading/data/training.Rsave")
dat.all <- training

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

# -------------------

frac <- function(x) { x-trunc(x) }

# Create hist of fractional part of bids, asks
plotPriceFractionHistogram <- function(in.dat, in.tag) { 

    asks      <- cbind(in.dat[all.asks]) # (instances) x (100 timeperiods )
    bids      <- cbind(in.dat[all.bids])  
    asks.bids <- as.matrix(cbind(asks,bids))
    print(typeof(asks.bids))
    print(dim(asks.bids))
    asks.bids.fractions <- frac(asks.bids)
    hist( asks.bids.fractions, 100, main=in.tag)
}

# --- main()

pdf(file=PLOTFILE)
par(mfrow=c(2,2)) # 2x2 matrix of plots 

# first do processing on ALL data, broken down by buys/sells
for(initiator in initiators) {
    print("Subsetting data")
    initiator.mask <- dat.all$initiator == initiator
    dat <-  dat.all[ initiator.mask ,] 
    tag <-  paste("security_id: ALL", "initiator:", initiator)
    print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
    plotPriceFractionHistogram(dat,tag)
}

# now do processing on each stock individually, broken down by buys/sells
for(initiator in initiators) {
    initiator.mask <- dat.all$initiator == initiator
    for(security_id in security_ids) {
        security_id.mask <- dat.all$security_id == security_id
        dat <-  dat.all[ initiator.mask & security_id.mask ,] 
        tag <-  paste("security_id:", security_id, "initiator:", initiator)
        print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
        plotPriceFractionHistogram(dat,tag)
    }
}

