
pdf(file="hist-intraday-deviations.pdf")
par(mfrow=c(2,2))

my.hist <- function(x, tag) {
    title <- paste("Hist Log10 Abs", tag)
    hist(log10(abs(x)), main=title, 50)
}

train <- readRDS("../data/train.RData")

rp2 <- train$Ret_PlusTwo

returns <- train[, paste("Ret_", c(2:180), sep="")]

returns.sd          <- apply(returns, 1, sd)
returns.meanabs     <- apply(returns, 1, function(x) mean(  abs(x)))
returns.medianabs   <- apply(returns, 1, function(x) median(abs(x)))
returns.sumabs      <- apply(returns, 1, function(x) sum(   abs(x)))

rp2.norm.sd         <- rp2 / returns.sd
rp2.norm.meanabs    <- rp2 / returns.meanabs
rp2.norm.medianabs  <- rp2 / returns.medianabs
rp2.norm.sumabs     <- rp2 / returns.sumabs

my.hist(returns.sd,        tag="sd returns" )
my.hist(returns.meanabs,   tag="mean abs returns")
my.hist(returns.medianabs, tag="median abs returns")
my.hist(returns.sumabs,    tag="sum abs returns")

my.hist(rp2.norm.sd,        tag="Ret_PlusTwo / sd")
my.hist(rp2.norm.meanabs,   tag="Ret_PlusTwo / mean abs returns")
my.hist(rp2.norm.medianabs, tag="Ret_PlusTwo / median abs returns")
my.hist(rp2.norm.sumabs,    tag="Ret_PlusTwo / sum abs returns")

my.hist(rp2, tag="Ret_PlusTwo")

