# Calculate best RMSE possible using a constant + slope fit for bid/ask

load(file="/home/chefele/AlgoTrading/data/training.Rsave") 
#load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- training # probe or training

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

# optimum RMSE using a constant bid/ask is just the average of bids/asks
USE_OPTIMUM <- TRUE
if(USE_OPTIMUM) {
    # using just bid/ask avg    : 0.7497644 RMSE on probe, 0.7918093 on training  
    # using bid/ask avg + slope : 0.5030627 RMSE on probe, 0.5185191 on training
    # so adding slope gives some improvement

    asks <- as.matrix(cbind(in.dat[post.asks]))
    bids <- as.matrix(cbind(in.dat[post.bids]))
    ask.means <- rowMeans( asks ) # a vector, not matrix
    bid.means <- rowMeans( bids ) 

    xt <- post.tperiods - mean(post.tperiods) # vector, not matrix 
    slope.asks <- rowSums(t(xt*t(asks-ask.means)))/sum(xt*xt)
    slope.bids <- rowSums(t(xt*t(bids-bid.means)))/sum(xt*xt)

    preds[post.asks] <- ask.means + outer(slope.asks, xt) 
    preds[post.bids] <- bid.means + outer(slope.bids, xt)

} else { # use naive predictor: ask/bid at t=50 
    # gets RMSE of 1.269548 on probe,  1.338763 on training 
    preds[post.asks] <- in.dat["ask50"] 
    preds[post.bids] <- in.dat["bid50"]
}

# ------------------- evaluate RMSE

preds.matrix   <- as.matrix(cbind(preds[post.bidasks]))
actuals.matrix <- as.matrix(cbind(in.dat[post.bidasks]))
err.matrix <- preds.matrix - actuals.matrix

rmse <- sqrt(mean(err.matrix^2))
print(rmse)

stop()

# now show how the error is distributed -- by rows 

mse.by.row <- rowMeans( err.matrix^2 ) 
sec_id <- in.dat$security_id
mse.by.security_id <- tapply(mse.by.row, sec_id, sum)
 
print(sort(mse.by.security_id, decreasing=TRUE))
print(sort(mse.by.security_id, decreasing=TRUE) / sum(mse.by.security_id) ) 
print( cumsum(sort(mse.by.security_id, decreasing=TRUE)) / sum(mse.by.security_id) )


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


