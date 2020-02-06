load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
dat <- probe

pre.tperiods   <- 1:50
mkNames        <- function(tag, periods) { paste(tag, as.character(periods), sep="") }
pre.times      <- mkNames("time", pre.tperiods)

parseHMS <- function(timeString) { strptime(timeString, format="%H:%M:%OS") }

pre.timestamps  <-   cbind(dat[,pre.times])

nuniq <- function(x) { length(unique(x)) }

pre.nuniqs   <-  apply( pre.timestamps, 1, nuniq)

pdf(file="unique_timestamps.pdf")
hist(pre.nuniqs, 400, main="Histogram of Number of Unique Timestamps (T1..T50)" )



