# mopen.naive.R 
# Reads a prediction file & overwrites predictions in the first N minutes with naive predictor predictions

# invoke with:  cat mopen.naive.R | R --vanilla --args <PREDS_FILE>  <PREDS_FILE_TYPE> <MARKET_OPEN_WINDOW>

# PREDS_FILE_TYPE = probe | testing
# MARKET_OPEN_WINDOW = seconds to use naive predictor for after the market open

# --- configurable constants

PREDS_FILE         <-            commandArgs(trailingOnly=TRUE)[1]  # must be probe file predictions
PREDS_FILE_TYPE    <-            commandArgs(trailingOnly=TRUE)[2]  # type of file 
MARKET_OPEN_WINDOW <- as.integer(commandArgs(trailingOnly=TRUE)[3]) # in seconds 

PROBE_FILE   <- "/home/chefele/AlgoTrading/data/probe.Rsave"
TESTING_FILE <- "/home/chefele/AlgoTrading/data/testing.Rsave"

# --- internal constants 

pre.tperiods  <- 1:50
post.tperiods <- 51:100
t.event <- 50

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

event.ask <- mkNames("ask", t.event)
event.bid <- mkNames("bid", t.event)

# --- check for valid mode
if(PREDS_FILE_TYPE!="probe" & PREDS_FILE_TYPE!="testing")  {
    stop("*** Bad file type; must be probe or testing")
}

# --- get the data

load(file=PROBE_FILE)
load(file=TESTING_FILE)
preds <- read.csv(PREDS_FILE)

# --- RMSE functions
getPrices <- function(df1)      { as.matrix(cbind(df1[post.bidasks])) }
getSqErrs <- function(df1,df2)  { (getPrices(df1) - getPrices(df2))^2 } # returns error^2 matrix
getRMSE   <- function(df1)      { sqrt(mean(getSqErrs(df1,probe)))    }

# --- Evaluate original RMSE 
if(PREDS_FILE_TYPE == "probe") {
    rmse.original <- getRMSE(preds)
    print( paste("Original RMSE of:", PREDS_FILE,"=", as.character(rmse.original)))
}

# --- get time of each event, and use naive predictor (bid/ask51...100 <- bid/ask50) if near market open 

parseHM  <- function(timeString) { strptime(timeString, format="%H:%M") } # hm in seconds, truncated hr & minute
if(PREDS_FILE_TYPE == "probe"   )  { hm <- parseHM(probe$time49)   } 
if(PREDS_FILE_TYPE == "testing" )  { hm <- parseHM(testing$time49) } 
hm.bin   <- as.numeric(hm - min(hm))      # make times relative to the start of the trading day
mktopen  <- hm.bin <= MARKET_OPEN_WINDOW

# --- overwite existing predictions with naive predictor 
if(PREDS_FILE_TYPE == "probe") {
    preds[mktopen,post.bids] <- probe[mktopen,event.bid]
    preds[mktopen,post.asks] <- probe[mktopen,event.ask]
} 
if(PREDS_FILE_TYPE == "testing") {
    preds[mktopen,post.bids] <- testing[mktopen,event.bid]
    preds[mktopen,post.asks] <- testing[mktopen,event.ask]
} 
print(paste("Modified:", as.character(sum(mktopen)), "prediction rows"))

# --- show updated RMSE if probe predictions
if(PREDS_FILE_TYPE == "probe") {
    print("Predictions updated using naive predictor at market open")
    rmse.updated <- getRMSE(preds)
    print( paste("Updated RMSE of:", PREDS_FILE,"=", as.character(rmse.updated)))
    print( paste("RMSE improvement:", as.character(rmse.original - rmse.updated)))
}

# --- write out the new version of testing | probe   file
if(PREDS_FILE_TYPE == "testing" | PREDS_FILE_TYPE == "probe" ) {
    fname <- paste("mopen_out.", PREDS_FILE, sep="")
    write.csv(preds, file=fname, quote=FALSE, row.names=FALSE, col.names=TRUE)
    print(paste("Wrote updated file to:", fname))
}

# finis 
