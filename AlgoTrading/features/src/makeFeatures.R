# ---- load data for testing...
#load("/home/chefele/AlgoTrading/data/probe.Rsave")
#dat <- probe
#load("/home/chefele/AlgoTrading/data/training.Rsave")
#dat <- training 

# ----------- utility functions

rowCor   <- function(x,y) { # Correlation between matching rows in X and Y
    x.ctr <- x - rowMeans(x) 
    y.ctr <- y - rowMeans(y) 
    x.sd  <- sqrt(rowSums(x.ctr * x.ctr)) 
    y.sd  <- sqrt(rowSums(y.ctr * y.ctr))
    EPS   <- 0.001
    x.sd[x.sd<EPS] <- EPS # prevents /0
    y.sd[y.sd<EPS] <- EPS
    rowcors <- rowSums( x.ctr*y.ctr ) / ( x.sd*y.sd ) 
    return(rowcors)
}

tslope <- function(x) { # slope of least-squares fit line of prices(x) vs time(t)
    ts      <- 1:50     # event time periods before shock trade
    ts.ctr  <- ts - mean(ts)
    x.ctr   <- x  - mean(x)
    slope.vs.ts <- sum(x.ctr * ts.ctr) / sum(ts.ctr * ts.ctr)
    return(slope.vs.ts)
}

clamp    <- function(x,xlo,xhi)  { 
    x[x<xlo]<-xlo
    x[x>xhi]<-xhi
}

advanceDecline <- function(x)    { sum(diff(x)>0) - sum(diff(x)<0) } 
numTrades<- function(x)          { sum(x=="T") } 
parseHMS <- function(timeString) { strptime(timeString, format="%H:%M:%OS") }
parseHM  <- function(timeString) { strptime(timeString, format="%H:%M") }
numUniqs <- function(x)          { length(unique(x)) } # Number of unique values
                                    

# ----------- makeFeatures

makeFeatures <- function(dat) {   # Returns features derived from the raw data 

    # Original data the following columns:
    #   row_id, security_id, p_tcount, p_value, trade_vwap, trade_volume, initiator,
    #   transtype1, time1, bid1, ask1,  ...   transtype50,time50,bid50,ask50

    # Local constants 
    mkt.open    <- min(parseHMS(dat$time1))
    bid.names   <- paste("bid", as.character(1:50),sep="")
    ask.names   <- paste("ask", as.character(1:50),sep="")
    time.names  <- paste("time",as.character(1:50),sep="")
    transtype.names <- paste("transtype",as.character(1:50),sep="")
    bids        <- cbind( dat[,bid.names] )
    asks        <- cbind( dat[,ask.names] )
    spread      <- (asks - bids)
    spread.midpt<- (asks + bids)/2.

    df <- data.frame(row_id = dat$row_id) # df is dataframe for output features 
    df <- within(df, {
        # original features
        print("Including original features")
        p_tcount     <- dat$p_tcount
        p_value      <- dat$p_value
        trade_vwap   <- dat$trade_vwap
        trade_volume <- dat$trade_volume

        # vwap features
        print("Creating VWAP features")
        vwap.ask50 <- dat$trade_vwap - dat$ask50 
        vwap.bid50 <- dat$trade_vwap - dat$bid50

        # Bid/ask features
        print("Creating bid/ask features")
        # scale free?
        bids.uniqs <- apply(bids, 1, numUniqs)
        asks.uniqs <- apply(asks, 1, numUniqs)
        bids.advdec<- apply(bids, 1, advanceDecline)
        asks.advdec<- apply(asks, 1, advanceDecline)
        bidask.cor <- rowCor(asks, bids)
        # not scale free
        bids.sd    <- apply(bids, 1, sd)
        asks.sd    <- apply(asks, 1, sd)
        bid.slope  <- apply(bids, 1, tslope)
        ask.slope  <- apply(asks, 1, tslope)
        bidask.corXsd <- rowCor(asks, bids) * (bids.sd + asks.sd)
        bidask.range <- apply(asks,1,max) - apply(bids,1,min)

        # Spread features
        print("Creating spread features")
        spread.mean   <- apply(spread,1,mean) 
        spread.median <- apply(spread,1,median)
        spread.max    <- apply(spread,1,max)
        spread.min    <- apply(spread,1,min) # often the tick size
        spread.slope  <- apply(spread,1,tslope)
        spread.sd     <- apply(spread.midpt,1,sd)
        spread.pct    <- apply(100.*spread/spread.midpt,1,mean) 
        spread.uniqs  <- apply(spread,1,numUniqs)
        spread.sdpct  <- 100.* spread.sd / spread.mean

        # Time features 
        print("Creating time features")
        window.secs <- as.numeric( parseHMS(dat$time50) - parseHMS(dat$time1) )
        tevent.rate <- log10(1.0/(window.secs+1.0))
        tevent.rateXvwap <- log10(1.0/(window.secs+1.0)) *  dat$trade_vwap
        tevent.rateXsd   <- log10(1.0/(window.secs+1.0)) * (bids.sd + asks.sd)
        window.secs <- NULL # deletes temporary variable

        daysecs     <- as.numeric(parseHMS(dat$time50) - mkt.open) # seconds since market open
        daysecs.log    <- log10( daysecs + 1.0 )  # log of seconds since market open
        daysecs.logXsd <- log10( daysecs + 1.0 ) * (bids.sd + asks.sd)  

        time.uniqs  <- apply( cbind(dat[,time.names]), 1, numUniqs) # num unique timestamps
       
        # Volume features
        print("Creating volume features")
        ntrades <- apply( cbind(dat[,transtype.names]), 1, numTrades) # num trades in t1..50; quotes=50-ntrades
        trade.normvolume  <- ( dat$trade_volume / dat$p_tcount )
        trade.normvalue   <- ( dat$trade_volume * dat$trade_vwap / dat$p_value )

        ntradesXvwap <- apply( cbind(dat[,transtype.names]), 1, numTrades) * dat$trade_vwap
        trade.normvolumeXvwap  <- ( dat$trade_volume / dat$p_tcount ) * dat$trade_vwap
        trade.normvalueXvwap   <- ( dat$trade_volume * dat$trade_vwap / dat$p_value ) * dat$trade_vwap

        # Relative price impact models below are based on models seen in various papers 
        print("Creating price impact features")
        impact.sdvolume     <-(     (trade.normvolume) * (bids.sd + asks.sd) )
        impact.sdvalue      <-(     (trade.normvalue ) * (bids.sd + asks.sd) )
        impact.sdsqrtvolume <-( sqrt(trade.normvolume) * (bids.sd + asks.sd) )
        impact.sdsqrtvalue  <-( sqrt(trade.normvalue ) * (bids.sd + asks.sd) )

    }) # end of within(df,{...})

    print(head(df))
    print(nrow(df))
    return(df)

    #pdf(file="makeFeatures.pdf")
    #for(col in names(df)) {
    #    hist(df[,col],200, main=col)
    #    plot(sort(df[,col]),type="l", main=col)
    #}


    # Other possible metrics / approaches:
    #  Per security statistics?
    #  Per security&day statistics? (e.g. group by security&p_tcount)
    #    Buys vs sells of this security on this day
    #    vwap / mean_vwap for this security on this day 
    #  Use entropy for anything?

}


# --------TESTING CODE

# load("/home/chefele/AlgoTrading/data/training.Rsave")
# load("/home/chefele/AlgoTrading/data/testing.Rsave")
# load("/home/chefele/AlgoTrading/data/probe.Rsave")
# dummy <- makeFeatures(probe)



