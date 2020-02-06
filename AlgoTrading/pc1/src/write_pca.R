# --- configurable constants

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

# Take a PCA of the concatenated bid/ask prices vs time & 
# then write the first principal componenet 
writePrComp <- function(in.dat, in.tag, fout) { 
    asks1 <- cbind(in.dat[post.asks])  # 1 row/event, cols are time periods
    bids1 <- cbind(in.dat[post.bids])  
    asks.bids <- t(as.matrix(cbind(asks1, bids1)))  # now rows=time, cols=events  

    prcomp.asks.bids <- prcomp(asks.bids, center=TRUE, scale=TRUE)
    print(summary(prcomp.asks.bids))

    pcs <- prcomp.asks.bids$x
    asks.pc1 <- pcs[1 : ncol(asks1), "PC1"]
    bids.pc1 <- pcs[ (ncol(asks1)+1) : (ncol(asks1)+ncol(bids1)) , "PC1"]  
    
    out.df <- data.frame(t=post.tperiods, asks=asks.pc1, bids=bids.pc1)
    write.csv(out.df, file=fout, row.names=FALSE, quote=FALSE)
}

# --- main()

#first do processing on ALL data, broken down by buys/sells
for(initiator in initiators) {
    print("Subsetting data")
    initiator.mask <- dat.all$initiator == initiator
    dat <-  dat.all[ initiator.mask ,] 
    tag <-  paste("security_id: ALL", "initiator:", initiator)
    print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))

    print("Writing PCA")
    outfilename <- paste("write_pca_init_",initiator,".csv",sep="")
    writePrComp(dat, tag, outfilename)
}

stop()

# now do processing on each stock individually, broken down by buys/sells
for(initiator in initiators) {
    initiator.mask <- dat.all$initiator == initiator
    for(security_id in security_ids) {
        security_id.mask <- dat.all$security_id == security_id
        dat <-  dat.all[ initiator.mask & security_id.mask ,] 
        tag <-  paste("security_id:", security_id, "initiator:", initiator)
        print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
        # writePrComp(dat, tag, all.tperiods)
    }
}


