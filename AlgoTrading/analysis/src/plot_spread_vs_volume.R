# Plot mean spreads vs mean event rate

#load(file="/home/chefele/AlgoTrading/data/training.Rsave") 
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- probe # probe or training

pre.tperiods  <- 1:50
post.tperiods <- 51:100
all.tperiods  <- 1:100
event.tperiod <- 49

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
all.bids  <- mkNames("bid", all.tperiods)
all.asks  <- mkNames("ask", all.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

# ------------------- 

parseHMS <- function(timeString) { strptime(timeString, format="%H:%M:%OS") }

# ------------------- 

asks <- as.matrix(cbind(in.dat[,all.asks]))
bids <- as.matrix(cbind(in.dat[,all.bids]))

spreads <- asks - bids
midspreads <- (asks+bids)/2
norm.spreads <- spreads/midspreads 
avg.norm.spreads <- rowMeans(norm.spreads)
avg.norm.spreads <- tapply(avg.norm.spreads,    in.dat$security_id, mean)

relative.volume <- in.dat$p_tcount
relative.volume <- tapply(relative.volume ,    in.dat$security_id, mean)

pdf(file="plot_spread_vs_volume.pdf")
plot(   log10(relative.volume), log10(avg.norm.spreads), 
        main="Avg Normalized Spread vs Relative Volume (One Pt Per Security_Id)",
        xlab="log10 Avg Relative Volume (Avg p_tcount per security)",
        ylab="log10 Normalized Spread (Averaged per security)"
)

