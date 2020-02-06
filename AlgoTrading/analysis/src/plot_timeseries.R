TESTDATA  <- "/home/chefele/AlgoTrading/data/probe.Rsave"
PLOTOUT   <- "plot_timeseries.pdf"
NPLOTS    <- 100
tperiods  <- 1:100
tEvent    <- 50
ask.names <- paste("ask",as.character(tperiods),sep="")
bid.names <- paste("bid",as.character(tperiods),sep="")

pdf(PLOTOUT)
par(mfrow=c(2,2))

load(TESTDATA) # probe, with answers 
tst <- probe

row.ids   <- sample(tst$row_id, NPLOTS, replace=F)
for(row.id in row.ids) { 
    r <- tst[row.id==tst$row_id,] 
    rowinfo <- paste(  "row_id:",     as.character(r$row_id),
                       "security_id:",as.character(r$security_id),
                       "init.:",  as.character(r$initiator) 
               )     
    asks <- cbind( r[ask.names] ) 
    bids <- cbind( r[bid.names] ) 
    preevent.midspread <- (r$bid48+r$ask48)/2.0
    event.midspread    <- (r$bid50+r$ask50)/2.0
    event.spread       <- (r$ask50-r$bid50)

    spreads <- asks - bids
    spread.midpt <- (bids+asks) / 2.0 

    print(rowinfo)

    # plot raw bids & asks vs time
    plot( tperiods, asks, main=rowinfo, type="b",  
          xlab="Time Period", ylab="Price", pch=16,  
          ylim=c( min(asks,bids), max(asks,bids) ) 
        )
    lines(tperiods, bids, type="b", lty="dashed")
    abline(v=tEvent,             lty="dotted")
    abline(h=event.midspread,    lty="dotted")

    # plot midpoint of spread vs time
    plot( tperiods, spread.midpt, main="Spread Midpt", type="b", xlab="Time Period", ylab="Price")
    abline(v=tEvent,             lty="dotted")
    abline(h=event.midspread,    lty="dotted")

    # plot spread vs time
    plot( tperiods, spreads, main="Spread", type="b", xlab="Time Period", ylab="Price")
    abline(v=tEvent,             lty="dotted")
    abline(h=event.spread,       lty="dotted")

    plot(0:1,0:1, main="BLANK")

}
