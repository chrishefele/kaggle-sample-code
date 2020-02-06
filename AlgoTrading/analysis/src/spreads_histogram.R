# % Spreads histogram 

#load(file="/home/chefele/AlgoTrading/data/training.Rsave") 
load(file="/home/chefele/AlgoTrading/data/probe.Rsave")
in.dat <- probe # probe or training

pre.tperiods  <- 1:50
post.tperiods <- 51:100
all.tperiods  <- 1:100

mkNames   <- function(bidask, periods) { paste(bidask, as.character(periods), sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
all.bids  <- mkNames("bid", all.tperiods)
all.asks  <- mkNames("ask", all.tperiods)
post.bidasks <- c(rbind(post.bids, post.asks))

# ------------------- create spreads histogram 

asks <- as.matrix(cbind(in.dat[all.asks]))
bids <- as.matrix(cbind(in.dat[all.bids]))
spreads <- asks - bids
midspreads <- (asks+bids)/2
norm.spreads <- spreads/midspreads 

pdf(file="spreads_histogram.pdf")

hist(log10(norm.spreads),200, main="Hist of log10(Spread/MidSpread)")
hist(norm.spreads[norm.spreads<=0.01],200, main="Hist of Spread/MidSpread <=0.01")
hist(norm.spreads[norm.spreads >0.01],200, main="Hist of Spread/MidSpread >0.01 ")
hist(norm.spreads[norm.spreads >0.1],200, main="Hist of Spread/MidSpread >0.1 ")

plot(sort(log10(norm.spreads)),type="l",main="Sorted log10(Spread/MidSpread)")

print(sum(norm.spreads<=0.01))
print(sum(norm.spreads >0.01))
print(sum(norm.spreads >0.1))



