# Tabulate RMSE distribution assuming a constant predictor 

load(file="/home/chefele/AlgoTrading/data/training.Rsave") 
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- training  # or training

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

# RMSE of below = 1.269548 t=50
preds[post.bids] <- in.dat["bid50"] # overwrite new bid columns with prediction data
preds[post.asks] <- in.dat["ask50"] # overwrite new ask columns with prediction data

# ------------------- evaluate RMSE

preds.matrix   <- as.matrix(cbind(preds[post.bidasks]))
actuals.matrix <- as.matrix(cbind(in.dat[post.bidasks]))
err.matrix <- preds.matrix - actuals.matrix

rmse <- sqrt(mean(err.matrix^2))
print(rmse)

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


