# --- configurable constants

PLOTFILE <- "plot_tevents.pdf"

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
    plot(times,xlab="event#",ylab="daysecond", main=in.tag, type="l")
}

# --- main ----

print("Now plotting ")
pdf(file=PLOTFILE)
par(mfrow=c(2,2)) # 2x2 matrix of plots 

if(FALSE) {
for(initiator in initiators) {
    print("Subsetting data")
    initiator.mask <- dat.all$initiator == initiator
    dat <-  dat.all[ initiator.mask ,] 
    tag <-  paste("security_id: ALL", "initiator:", initiator)
    print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
    plotTEvents(dat, tag)
}
}

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

