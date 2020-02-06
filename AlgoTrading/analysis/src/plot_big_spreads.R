# Plot spreads histogram 

SPREAD_THRESHOLD <- 0.01

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

# ------------------- create spreads histogram 

twindow <- all.tperiods
asks <- as.matrix(cbind(in.dat[,all.asks]))
bids <- as.matrix(cbind(in.dat[,all.bids]))
spreads <- asks - bids
midspreads <- (asks+bids)/2
norm.spreads <- spreads/midspreads 
mask <- rowSums( norm.spreads > SPREAD_THRESHOLD ) > 0
dat <- in.dat[mask ,]  # plot large spreads only

pdf(file="plot_big_spreads.pdf")
par(mfrow=c(2,2)) # 2x2 matrix of plots 

for(row_id in 1:nrow(dat) ) {

    asks <- as.matrix(cbind(dat[row_id, all.asks]))
    bids <- as.matrix(cbind(dat[row_id, all.bids]))
    spreads <- asks - bids
    midspreads <- (asks+bids)/2
    norm.spreads <- spreads/midspreads 
    name.tag <- paste( "sec_id:", as.character(dat[row_id,]$security_id), 
                       "row:",    as.character(dat[row_id,]$row_id),
                       "t1:",     as.character(dat[row_id,]$time1 )
                     )

    print(name.tag)
    print(100*row_id/nrow(dat))
    # plot bids, asks, mid-spread vs time
    plot(twindow, asks, main=name.tag, type="l", 
         xlab="Time Period", ylab="Price", 
         ylim=c(min(asks,bids), max(asks,bids))
    )
    lines(twindow, bids,      type="l", lty="solid")
    lines(twindow, midspreads, type="l", lty="dashed" ) 
    abline(v=event.tperiod, lty="dotted")

}

