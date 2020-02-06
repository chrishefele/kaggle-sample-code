# plot predictions
# invoke with:   cat plot-predictions.R | R --vanilla --args <INFILE> <NUMPLOTS>

# -------------- Constants to tweak & tune

INFILE   <-             commandArgs(trailingOnly=TRUE)[1]
NUMPLOTS <-  as.integer(commandArgs(trailingOnly=TRUE)[2])

PLOTFILE <- paste(INFILE,".pdf",sep="") 
t.all    <- 51:100   # time periods covered in submission file

# -------------- main()

# load the data, but cache for speed in case of repeated runs
cache.file <- paste(INFILE,".Rsave",sep="")
if(!file.exists(cache.file)) {
    submission <- read.csv(INFILE,header=TRUE)
    save(submission, file=cache.file)
}
load( paste(INFILE,".Rsave",sep="") )

varNames <- function(bidask, trange) { paste(bidask, as.character(trange),sep="") }
bidask.names <- as.vector(rbind( varNames("bid",t.all), varNames("ask",t.all)))

pdf(file=PLOTFILE)
par(mfrow=c(2,2))

for(n in 1:NUMPLOTS) {
    #if(n %% PLOT_MOD != 0) next  # ****** ADDED  TO JUST GET PLOTS 
    bids.all     <- as.numeric(submission[n,varNames("bid",t.all)])
    asks.all     <- as.numeric(submission[n,varNames("ask",t.all)])
    print(paste("Plotting:",as.character(n)))
    y.upper <- max(bids.all, asks.all)
    y.lower <- min(bids.all, asks.all)
    plot.title <- paste( "row_id:", as.character(submission[n,"row_id"]) )
    plot(  t.all, bids.all, main=plot.title,type="p", ylab="ask & bid prices", ylim=c(y.lower,y.upper) )
    points(t.all, asks.all)
}

print(paste("Wrote plots to:",PLOTFILE))
print("Done.")

