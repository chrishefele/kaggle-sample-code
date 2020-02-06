#load(file="/home/chefele/AlgoTrading/data/training.Rsave")
PREDS_PROBE_OUT <- "consts.probe.csv"
load(file="/home/chefele/AlgoTrading/data/testing.Rsave")
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- probe

pre.tperiods  <- 1:50
post.tperiods <- 51:100

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

# ------------------- make predictions 

preds <- data.frame(row_id=in.dat$row_id)
preds[,post.bidasks] <- 0  # create new columns in right sequence

bids <- cbind(in.dat[pre.bids])
asks <- cbind(in.dat[pre.asks])
spreads <- asks-bids
spreads.mean <-  rowMeans(spreads) 

buyers  <- in.dat$initiator == "B"
sellers <- in.dat$initiator == "S"
buyers.and.sellers <- buyers | sellers 

# for buys 
#preds[buyers, post.asks]  <- in.dat[buyers,  c("ask50")] 
#preds[buyers, post.bids]  <- in.dat[buyers,  c("ask50")] - spreads.mean[buyers]
# for sells
#preds[sellers, post.bids] <- in.dat[sellers, c("bid50")] 
#preds[sellers, post.asks] <- in.dat[sellers, c("bid50")] + spreads.mean[sellers]

# RMSE of below = 1.269548 t=50
preds[post.bids] <- in.dat["bid50"] # overwrite new bid columns with prediction data
preds[post.asks] <- in.dat["ask50"] # overwrite new ask columns with prediction data

# RMSE = 1.452733 t=49 or 48
# RMSE = 1.568093 t=40

# ------------------- evaluate RMSE

scoreRMSE <- function(preds, actuals, eval.rows, eval.cols) {
    preds.matrix   <- as.matrix(cbind(preds[eval.rows, eval.cols]))
    actuals.matrix <- as.matrix(cbind(actuals[eval.rows, eval.cols]))
    rmse <- sqrt(mean( (preds.matrix-actuals.matrix)^2 ))
    return(rmse)
} 

preds.matrix   <- as.matrix(cbind(preds[post.bidasks]))
actuals.matrix <- as.matrix(cbind(probe[post.bidasks]))
rmse <- sqrt(mean( (preds.matrix-actuals.matrix)^2 ))
print(rmse)

print( scoreRMSE(preds, probe, buyers.and.sellers, post.bidasks) ) 

print( scoreRMSE(preds, probe, buyers,  post.asks) ) 
print( scoreRMSE(preds, probe, buyers,  post.bids) ) 
print( scoreRMSE(preds, probe, sellers, post.asks) ) 
print( scoreRMSE(preds, probe, sellers, post.bids) ) 

write.csv(preds, file=PREDS_PROBE_OUT, quote=FALSE, row.names=FALSE, col.names=TRUE)

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


