
SUMABS.TO.DAILYRET <- 0.19

test2 <- readRDS("../data/test_2.RData")
test2[is.na(test2)] <- 0

rm2 <- test2$Ret_MinusTwo

col.select <- paste("Ret", 2:120, sep="_")
ret.sumabs <- rowSums(test2[,col.select])

groups <- unique(test2$Feature_7)

rscales <- c(1:100)/100 * 2

for(rscale in rscales) {

    errs.pred <- c()
    wins.pred <- c()
    errs.gain <- c()

    for(loop in 1:1000) {

        group.pick   <- sample(groups, 1)
        group.select <- 1 * (group.pick == test2$Feature_7)

        preds        <- rscale * ret.sumabs * SUMABS.TO.DAILYRET * group.select 
        err.zero     <- sum(abs(rm2-0))
        err.pred.pos <- sum(abs(rm2 -  preds))
        err.pred.neg <- sum(abs(rm2 - -preds))
        err.pred     <- min(err.pred.pos, err.pred.neg)
        err.gain     <- err.zero - err.pred 

        errs.pred    <- c(errs.pred, err.pred)
        wins.pred    <- if(err.pred < err.zero) { c(wins.pred, 1) } else { c(wins.pred, 0) }
        errs.gain    <- c(errs.gain, err.gain)
    }
    cat("scale: ",     rscale, 
        #"mean err: ",  mean(errs.pred), 
        "mean gain: ", mean(errs.gain), 
        "median gain: ", median(errs.gain), 
        "max  gain: ", max(errs.gain), 
        "prob win: ",  mean(wins.pred), "\n")

}
