# tsmooth --- by CJH - 12/12/11

# This is a R script to post-process submission files for the Kaggle Algorithmic Trading Challenge
# - It smooths submission file bid/asks across time (ignoring the first few time points)
# - It outputs RMSE difference between the old and new submission file 
# - It outputs a new submission file  
# It takes ~90 minutes to run

# -------------- Constants to tweak & tune

# usage:   cat tsmooth.R | R --vanilla --args <INFILE> <OUTFILE> 
INFILE <- commandArgs(trailingOnly=TRUE)[1]
OUTFILE<- commandArgs(trailingOnly=TRUE)[2]
HEADERS<- TRUE # headers on infile

LOESS_SPAN <- 0.75   # controls smoothing, smaller=less smoothing; default=0.75

t.all    <- 51:100   # time periods covered in submission file
t.nofit  <- 51:55    # time periods to NOT smooth (i.e. near the shock trade)
t.tofit  <- 56:100   # time periods to fit with a LOESS curve 

# -------------- main()

# load the data, but cache for speed in case of repeated runs
cache.file <- paste(INFILE,".Rsave",sep="")
if(!file.exists(cache.file)) {
    submission <- read.csv(INFILE,header=HEADERS)
    save(submission, file=cache.file)
}
load( paste(INFILE,".Rsave",sep="") )

varNames <- function(bidask, trange) { paste(bidask, as.character(trange),sep="") }
bidask.names <- as.vector(rbind( varNames("bid",t.all), varNames("ask",t.all)))
if(!HEADERS) names(submission) <- c("row_id", bidask.names)

bidask.outrows <- cbind(submission[, c("row_id",bidask.names) ]) # will overwrite with new data
bidask.original <- as.matrix(bidask.outrows)

for(n in 1:nrow(submission)) {
    print(n)

    bids.all     <- as.numeric(submission[n,varNames("bid",t.all)])
    bids.tofit   <- as.numeric(submission[n,varNames("bid",t.tofit)])
    bids.nofit   <- as.numeric(submission[n,varNames("bid",t.nofit)])

    asks.all     <- as.numeric(submission[n,varNames("ask",t.all)])
    asks.tofit   <- as.numeric(submission[n,varNames("ask",t.tofit)])
    asks.nofit   <- as.numeric(submission[n,varNames("ask",t.nofit)])

    bids.fitted <- predict( loess(bids.tofit ~ t.tofit, span=LOESS_SPAN) )
    asks.fitted <- predict( loess(asks.tofit ~ t.tofit, span=LOESS_SPAN) )

    bids.curve  <- c(bids.nofit, bids.fitted)
    asks.curve  <- c(asks.nofit, asks.fitted)
    bidask.outrows[n, bidask.names] <- as.vector(rbind(bids.curve, asks.curve)) #overwrites

    # if(n %% PLOT_MOD == 0) {
    if(FALSE) {
        print(paste("Plotting:",as.character(n)))
        y.upper <- max(bids.tofit, bids.nofit, asks.tofit, asks.nofit)
        y.lower <- min(bids.tofit, bids.nofit, asks.tofit, asks.nofit)
        plot.title <- paste( "row_id:", as.character(submission[n,"row_id"]) )
        plot(  t.all, bids.all, main=plot.title,type="p", ylab="ask & bid prices", ylim=c(y.lower,y.upper) )
        points(t.all, asks.all)
        lines( t.all, bids.curve)
        lines( t.all, asks.curve)
    }
}

write.csv(bidask.outrows, file=OUTFILE, quote=FALSE, row.names=FALSE)

bidask.tsmoothed <- as.matrix(bidask.outrows)
errs <- bidask.original - bidask.tsmoothed
rmse <- sqrt(mean(errs*errs))

print(paste("RMSE change from smoothing:",as.character(rmse)))
print(paste("Wrote new submission to:",OUTFILE))
print("Done.")

