# Calculate error distribution across time assuming a constant predictor for bid/ask

#load(file="/home/chefele/AlgoTrading/data/training.Rsave") 
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- probe # probe or training

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
USE_OPTIMUM <- FALSE
if(USE_OPTIMUM) {
    # gets RMSE of 0.7497644 on probe, 0.7918093 on training 
    preds[post.asks] <- rowMeans( as.matrix(cbind(in.dat[post.asks])))
    preds[post.bids] <- rowMeans( as.matrix(cbind(in.dat[post.bids])))
} else { # use naieve predictor
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

# now show how the error is distributed over time (H:M=hour:minute)

parseHM  <- function(timeString) { strptime(timeString, format="%H:%M") }
hm <- parseHM(in.dat$time49)
hm.min <- min(hm)
hm.by.row <- hm - hm.min

mse.by.row <- rowMeans( err.matrix^2 ) 
mse.by.hm <- tapply(mse.by.row, hm.by.row, sum)
 
print(sort(mse.by.hm, decreasing=TRUE))
print(sort(mse.by.hm, decreasing=TRUE) / sum(mse.by.hm) ) 
print(cumsum(sort(mse.by.hm, decreasing=TRUE)) / sum(mse.by.hm) )

print(mse.by.hm)
print(mse.by.hm / sum(mse.by.hm)) 
print(cumsum(mse.by.hm) / sum(mse.by.hm) )

pdf("const_rmse_err_timedist.pdf")
plot(mse.by.hm / sum(mse.by.hm)) 
plot(cumsum(mse.by.hm) / sum(mse.by.hm) )



