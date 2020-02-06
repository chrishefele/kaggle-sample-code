
library(quantreg)


TEST2.FILE <- "../data/test_2.RData"
PLOT.FILE  <- "opt-2guess-test2.pdf"
SUMABS.TO.DAILYRET <- 0.19

test2 <- readRDS(TEST2.FILE)
test2[is.na(test2)] <- 0

pdf(file=PLOT.FILE)
#par(mfrow=c(2,2))

ret.cols   <- paste("Ret", 2:120, sep="_")
ret.sumabs <- rowSums(abs(test2[,ret.cols]))
rm2        <- test2[,"Ret_MinusTwo"]

errs.pred  <- c()
errs.zero  <- c()
pwins.pred <- c()

sumabs.scales <- c(1:100)/100 * (1E-1)

for(sumabs.scale in sumabs.scales) {

    ret.pred      <- sumabs.scale * ret.sumabs * SUMABS.TO.DAILYRET 
    err.pred.pos  <- sum(abs(rm2 -  ret.pred))
    err.pred.neg  <- sum(abs(rm2 - -ret.pred))
    err.pred      <- min(err.pred.pos, err.pred.neg)
    
    err.zero      <- sum(abs(rm2 - 0))

    errs.pred  <- c(errs.pred, err.pred)
    errs.zero  <- c(errs.zero, err.zero)

    cat("sumabs.scale: ", sumabs.scale, 
        " err.pred: ", err.pred, 
        " err.zero: ", err.zero, "\n")

}


plot(sumabs.scales, errs.pred, xlab="sumabs.scale", ylab="mean.error", type="l")
lines(sumabs.scales, errs.zero)

mask <- sumabs.scales <= 0.5

plot(sumabs.scales[mask], errs.pred[mask], xlab="sumabs.scale", ylab="mean.error", type="l")
lines(sumabs.scales[mask], errs.zero[mask])

