# pc1.R  -- predict first principal component, properly scaled & translated

PROBE_MODE <- FALSE # predict probe or testing dafa 

if(PROBE_MODE) { 
    OUTFILE <- "pc1.probe.csv" 
    load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
    in.dat <- probe
} else { 
    OUTFILE <- "pc1.testing.csv"
    load(file="/home/chefele/AlgoTrading/data/testing.Rsave")
    in.dat <- testing
}

pre.tperiods  <- 1:50
post.tperiods <- 51:100

mkNames   <- function(bidask, periods) { 
    paste(bidask, as.character(periods), sep="") 
}
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

makeBidAskDataFrame <- function(raw) {
    asks <- raw$asks
    bids <- raw$bids
    names(asks) <- post.asks
    names(bids) <- post.bids 
    bidasks <- c(bids, asks)
    #print("Raw bidasks")
    #print(bidasks)
    df <- data.frame(t(bidasks[post.bidasks]))
    return(df)
} # returns single row dataframe of pc1 bids & asks t51..t100

pc1b <- makeBidAskDataFrame( read.csv("write_pca_init_B.csv") )  # pc1 for buys,  single row dataframe
pc1s <- makeBidAskDataFrame( read.csv("write_pca_init_S.csv") )  # pc1 for sells, single row dataframe

# ------------------- make predictions 

# scale spreads to match t50 values to t51 (it's known that bid/ask50==bid/ask51) 
spread.dat50<- abs( in.dat$ask50 - in.dat$bid50 ) # vector
spread.pc1b <- abs( pc1b$ask51   - pc1b$bid51 )   # scalar
spread.pc1s <- abs( pc1s$ask51   - pc1s$bid51 )   # scalar 
flip <- -1 # flip, since original data pc1 data is inverted (for some reason)

buyers  <- in.dat$initiator == "B" 
sellers <- in.dat$initiator == "S" 

scale.b <- flip * spread.dat50[buyers]  / spread.pc1b 
scale.s <- flip * spread.dat50[sellers] / spread.pc1s 

preds <- data.frame(row_id=in.dat$row_id)
preds[,post.bidasks] <- 0 # creates new columns to fill 

preds[buyers,  post.bidasks] <- pc1b[,post.bidasks] # pc1b & pc1s 1-row, so repeats fill 50k times
preds[sellers, post.bidasks] <- pc1s[,post.bidasks] 

preds[buyers,  post.bidasks] <- preds[buyers,  post.bidasks]  * scale.b
preds[sellers, post.bidasks] <- preds[sellers, post.bidasks]  * scale.s

preds[buyers,  post.bidasks] <- preds[buyers,  post.bidasks] -  
                                preds[buyers,  "bid51"]      +
                                in.dat[buyers, "bid50"]
preds[sellers, post.bidasks] <- preds[sellers, post.bidasks] -
                                preds[sellers, "bid51"]      +
                                in.dat[sellers,"bid50"]

write.csv(preds, file=OUTFILE, row.names=FALSE, quote=FALSE)

# RMSE of below = 1.269548 t=50
# preds[post.bids] <- in.dat["bid50"] 
# preds[post.asks] <- in.dat["ask50"]

# RMSE of PC1 is 1.21 

# ------------------- evaluate RMSE
if(PROBE_MODE) {
    preds.matrix   <- as.matrix(cbind(preds[post.bidasks]))
    actuals.matrix <- as.matrix(cbind(probe[post.bidasks]))
    rmse <- sqrt(mean( (preds.matrix-actuals.matrix)^2 ))
    print(rmse)
}

stop()


# now do processing on each stock individually, broken down by buys/sells
for(initiator in initiators) {
    initiator.mask <- dat.all$initiator == initiator
    for(security_id in security_ids) {
        security_id.mask <- dat.all$security_id == security_id
        dat <-  dat.all[ initiator.mask & security_id.mask ,] 
        tag <-  paste("security_id:", security_id, "initiator:", initiator)
        # pass
    }
}


