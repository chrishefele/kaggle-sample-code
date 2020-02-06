# Plot error correlates

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

sid <- in.dat$security_id

asks    <- as.matrix(cbind(in.dat[,post.asks]))
bids    <- as.matrix(cbind(in.dat[,post.bids]))
asks.pre    <- as.matrix(cbind(in.dat[,pre.asks]))
bids.pre    <- as.matrix(cbind(in.dat[,pre.bids]))
spreads <- asks - bids
spreads.pre <- asks.pre - bids.pre
asks.errs  <- asks - asks[,1] # naive predictor
bids.errs  <- bids - bids[,1]
sqerrs  <- tapply( rowSums(asks.errs^2)+rowSums(bids.errs^2), sid, mean)


avg.spread <- tapply(rowMeans(spreads.pre), sid, mean)
spread.48 <- tapply( in.dat$ask48 - in.dat$bid48, sid, mean)
spread.49 <- tapply( in.dat$ask49 - in.dat$bid49, sid, mean)
spread.50 <- tapply( in.dat$ask50 - in.dat$bid50, sid, mean)
asks.sd <- tapply( apply(asks.pre,1,sd), sid, mean)
bids.sd <- tapply( apply(bids.pre,1,sd), sid, mean)
value   <- tapply( in.dat$p_value ,      sid, mean)
volume  <- tapply( in.dat$p_tcount,      sid, mean)
vwaps   <- tapply( in.dat$trade_vwap, sid, mean)
security.count <- tapply( table(in.dat$security_id)[as.character(in.dat$security_id)], sid, max ) 
jumps <- tapply( pmax( in.dat$ask50-in.dat$ask49, -(in.dat$bid50-in.dat$bid49)) , sid, mean)

pdf(file="plot_err_correlates.pdf")
plot(log(avg.spread), log(sqerrs))
plot(log(asks.sd), log(sqerrs))
plot(log(bids.sd), log(sqerrs))
plot(log(value), log(sqerrs))
plot(log(volume), log(sqerrs))
plot(log(vwaps), log(sqerrs))
plot(log(security.count), log(sqerrs))
plot(log(spread.48), log(sqerrs))
plot(log(spread.49), log(sqerrs))
plot(log(spread.50), log(sqerrs))
plot(log(jumps), log(sqerrs))

df <- data.frame(sqerrs=sqerrs, avg.spread=avg.spread, asks.sd=asks.sd, bids.sd=bids.sd, value=value, volume=volume, vwaps=vwaps, security.count=security.count, spread.48=spread.48, spread.49=spread.49, spread.50=spread.50, jumps=jumps)

print(cor(df))

