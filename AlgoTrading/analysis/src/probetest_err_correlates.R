#probetest_error_correlates

load(file="/home/chefele/AlgoTrading/data/testing.Rsave") 
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
load(file="/home/chefele/AlgoTrading/data/training.Rsave")

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

makeRatios <- function(in.dat) {
    sid       <- in.dat$security_id
    asks.pre  <- as.matrix(cbind(in.dat[,pre.asks]))
    bids.pre  <- as.matrix(cbind(in.dat[,pre.bids]))
    if( any(names(in.dat)=="ask51")) {
        asks.post <- as.matrix(cbind(in.dat[,post.asks]))
        bids.post <- as.matrix(cbind(in.dat[,post.bids]))
    } else {
        asks.post <- asks.pre * 0 + 1  # dummy data, since post-event data hidden 
        bids.post <- bids.pre * 0 + 1
    }
    spreads   <- asks.pre - bids.pre

    asks.errs  <- asks.post - asks.post[,1] # naive predictor
    bids.errs  <- bids.post - bids.post[,1]
    # sqerrs  <- tapply( rowSums(asks.errs^2)+rowSums(bids.errs^2), sid, mean) # ******** correlate to mean  error
    sqerrs  <- tapply( rowSums(asks.errs^2)+rowSums(bids.errs^2), sid, sum ) # ******** correlate to total error

    avg.spread<- tapply( rowMeans(spreads), sid, mean)
    spread.48 <- tapply( in.dat$ask48 - in.dat$bid48, sid, mean)
    spread.49 <- tapply( in.dat$ask49 - in.dat$bid49, sid, mean)
    spread.50 <- tapply( in.dat$ask50 - in.dat$bid50, sid, mean)
    asks.sd   <- tapply( apply(asks.pre,1,sd), sid, mean)
    bids.sd   <- tapply( apply(bids.pre,1,sd), sid, mean)
    value     <- tapply( in.dat$p_value ,      sid, mean)
    volume    <- tapply( in.dat$p_tcount,      sid, mean)
    vwaps     <- tapply( in.dat$trade_vwap, sid, mean)
    security.count <- tapply( table(in.dat$security_id)[as.character(in.dat$security_id)], sid, max ) 
    jumps <- tapply( pmax( in.dat$ask50-in.dat$ask49, -(in.dat$bid50-in.dat$bid49)) , sid, mean)
    counts.spread.50  <- security.count * spread.50
    counts.vwap       <- security.count * vwaps
    counts.asks.sd    <- security.count * asks.sd
    counts.bids.sd    <- security.count * bids.sd
    counts.bidasks.sd <- security.count * (asks.sd + bids.sd)/2.0

    df <- data.frame( 
                    sqerrs=sqerrs,
                    avg.spread=avg.spread, 
                    asks.sd=asks.sd, 
                    bids.sd=bids.sd, 
                    value=value, 
                    volume=volume, 
                    vwaps=vwaps, 
                    security.count=security.count, 
                    spread.48=spread.48, spread.49=spread.49, spread.50=spread.50, 
                    jumps=jumps,
                    counts.spread.50=counts.spread.50, 
                    counts.vwap=counts.vwap,
                    counts.asks.sd=counts.asks.sd, 
                    counts.bids.sd=counts.bids.sd,
                    counts.bidasks.sd=counts.bidasks.sd
                )
    return(df)
}

probe.stats   <- makeRatios(probe)
testing.stats <- makeRatios(testing)
training.stats <- makeRatios(training) # *************

print(cor(probe.stats))
print(cor(testing.stats))

print(cor(training.stats)) # ***********

pdf(file="probetest_error_correlates.pdf")

for(statname in names(probe.stats)) {
    print(statname)
    plot(log10(probe.stats[[statname]]), log10(probe.stats$sqerrs), main=paste("probe:",statname))
}

ratios <- probe.stats / testing.stats
for(ratio.name in names(ratios)) {
    print(ratio.name)
    if(ratio.name=="sqerrs") next  # no sqerr available for testing set 
    hist(ratios[[ratio.name]],100, main=paste("probe/test ratio:", ratio.name))
}


