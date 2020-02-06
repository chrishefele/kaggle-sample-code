
PLOTFILE <- "plot_vwap_vs_time50.pdf"

#load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
#dat.all <- probe
load(file="/home/chefele/AlgoTrading/data/training.Rsave")
dat.all <- training

parseHMS <- function(timeString) { 
    strptime(timeString, format="%H:%M:%OS") 
}

plotVWAPvsTime <- function(in.dat, in.tag) {
    time.objs <- parseHMS(in.dat$time50)
    times <- as.numeric(time.objs-min(time.objs)) 
    vwaps <- in.dat$trade_vwap 
    plot(times, vwaps, xlab="Event time (time50)",ylab="Event VWAP", main=in.tag, type="p")
    closeup.mask <- (times>=10000) & (times<=11000)
    plot(times[closeup.mask], vwaps[closeup.mask], 
         xlab="Event time (time50)",ylab="Event VWAP", main=in.tag, type="p")
}

# --- main ----

print("Now plotting ")
pdf(file=PLOTFILE)
par(mfrow=c(2,1))

security_ids <- sort(unique(dat.all$security_id))
for(security_id in security_ids) {
    security_id.mask <- dat.all$security_id == security_id
    dat <-  dat.all[ security_id.mask ,] 
    tag <-  paste("Security_ID:", security_id)
    print(paste("PROCESSING ", tag, "rows:", as.character(nrow(dat)) ))
    plotVWAPvsTime(dat,tag)
}

