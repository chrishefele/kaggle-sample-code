# Plot PCA of 50 time periods across all data rows to answer the questoin 
# of how many PCs (& thus modeing parameters) it takes to capture the time behavior

# --- configurable constants

PLOTFILE <- "plot_pca_rows_allvsbuysell.pdf"

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

# Take a PCA of the concatenated bid/ask prices vs time & 
# then plot the first 3 principal componenets vs time plus the scree
plotPrCompVsTime <- function(in.dat, in.tag) { 
    asks1 <- cbind(in.dat[post.asks])  # 1 row/event, cols are time periods
    bids1 <- cbind(in.dat[post.bids])  

    #asks.bids <- t(as.matrix(cbind(asks1, bids1)))  # now rows=time, cols=events  
    asks.bids <-   (as.matrix(cbind(asks1, bids1)))  # now rows=events, cols=time

    asks.bids <-   asks.bids - rowMeans(asks.bids)

    prcomp.asks.bids <- prcomp(asks.bids, center=TRUE, scale=TRUE)
    print(summary(prcomp.asks.bids))
    plot(prcomp.asks.bids, main="DataRows Principal Components Scree")

    # pcs <- prcomp.asks.bids$x
}


# --- main()

pdf(file=PLOTFILE)

# plot all buys & sells 
dat <-  dat.all
tag <-  paste("initiator: B&S")
print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
plotPrCompVsTime(dat, tag) 

# plot buys & sells seperately 
for(initiator in initiators) {
    print("Subsetting data")
    initiator.mask <- dat.all$initiator == initiator
    dat <-  dat.all[ initiator.mask ,] 
    tag <-  paste("initiator:", initiator)
    print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
    plotPrCompVsTime(dat, tag) 
}


