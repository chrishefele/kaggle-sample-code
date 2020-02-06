TARGET_SECURITY_ID <- 75
TESTDATA  <- "/home/chefele/AlgoTrading/data/probe.Rsave"
PLOTOUT   <- "plot_timeseries_security75.pdf"
tperiods  <- 1:100
tEvent    <- 50
ask.names <- paste("ask",as.character(tperiods),sep="")
bid.names <- paste("bid",as.character(tperiods),sep="")

pdf(PLOTOUT)
par(mfrow=c(2,2))

load(TESTDATA) # probe, with answers 
tst <- probe[probe$security_id==TARGET_SECURITY_ID,]

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }

calc.row.mses <- function(in.dat) {
    pre.tperiods  <- 1:50
    post.tperiods <- 51:100
    pre.bids  <- mkNames("bid", pre.tperiods)
    pre.asks  <- mkNames("ask", pre.tperiods)
    post.bids <- mkNames("bid", post.tperiods)
    post.asks <- mkNames("ask", post.tperiods)
    post.bidasks <- c(rbind(post.bids, post.asks))
    
    preds <- data.frame(row_id=in.dat$row_id)
    preds[,post.bidasks] <- 0  # create new columns in right sequence
    preds[post.bids] <- in.dat["bid50"] # overwrite new bid columns with prediction data
    preds[post.asks] <- in.dat["ask50"] # overwrite new ask columns with prediction data
    preds.matrix   <- as.matrix(cbind(preds[post.bidasks]))
    actuals.matrix <- as.matrix(cbind(in.dat[post.bidasks]))
    err.matrix <- preds.matrix - actuals.matrix
    return( rowMeans( err.matrix^2 ) )
}


row.ids   <- tst$row_id
print(head(row.ids))
tst$row.mses  <- calc.row.mses(tst)
print(head(tst$row.mses))
print(head(order(tst$row.mses, decreasing=TRUE)))
row.ids.msesort   <- row.ids[ order(tst$row.mses, decreasing=TRUE) ]
print(head(row.ids.msesort))

for(row.id in row.ids.msesort) {
    r <- tst[row.id==tst$row_id,] 
    rowinfo <- paste(   as.character(r$row_id),
                        as.character(r$security_id),
                        as.character(r$initiator),
                        r$time50,
                        paste("err",as.character(as.integer(r$row.mses)))
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
    plot( tperiods, asks, main=rowinfo, type="s",  
          xlab="Time Period", ylab="Price",   
          ylim=c( min(asks,bids), max(asks,bids) ) 
        )
    lines(tperiods, bids, type="s" )
    abline(v=tEvent,   lty="dotted")
    abline(h=r$ask50,  lty="dotted")
    abline(h=r$bid50,  lty="dotted")

    # plot spread vs time
    plot( tperiods, spreads, main="Spread", type="s", xlab="Time Period", ylab="Price")
    abline(v=tEvent,             lty="dotted")
    abline(h=event.spread,       lty="dotted")

}
