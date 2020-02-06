# --- configurable constants

PLOTFILE <- "plot_tprices.pdf"

#load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
#dat.all <- probe
load(file="/home/chefele/AlgoTrading/data/training.Rsave")
dat.all <- training

security_ids <- sort(unique(dat.all$security_id))
initiators   <- sort(unique(dat.all$initiator))

parseHMS <- function(timeString) { 
    strptime(timeString, format="%H:%M:%OS") 
}

plotTEvents <- function(in.dat, in.tag) {
    time.objs <- parseHMS(in.dat$time50)
    times <- as.numeric(time.objs-min(time.objs)) 
    event.vwaps <- in.dat$trade_vwap 
    plot(event.vwaps, xlab="event#",ylab="event vwap", main=in.tag, type="l")
}

# --- main ----

print("Now plotting ")
pdf(file=PLOTFILE)
par(mfrow=c(2,2)) # 2x2 matrix of plots 

# now do processing on each stock individually, broken down by buys/sells
for(initiator in initiators) {
    initiator.mask <- dat.all$initiator == initiator
    for(security_id in security_ids) {
        security_id.mask <- dat.all$security_id == security_id
        dat <-  dat.all[ initiator.mask & security_id.mask ,] 
        tag <-  paste("security_id:", security_id, "initiator:", initiator)
        print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
        plotTEvents(dat,tag)
    }
}

