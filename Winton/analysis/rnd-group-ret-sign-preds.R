

train <- readRDS("../data/train.RData")
train[is.na(train)] <- 0

wt  <- train$Weight_Daily
rp2 <- train$Ret_PlusTwo
rm2 <- train$Ret_MinusTwo

nonzeros <- 1
rscales  <- c(1:100) / 100 * 2

for(rscale in rscales) {

    signs <- rep(0, length(rm2))
    one.posns <- sample(1:length(rm2), nonzeros)
    signs[one.posns] <-  1
    errs.pred <- c()
    wins.pred <- c()
    errs.gain <- c()

    for(loop in 1:1000) {

        preds        <- rm2 * sample(signs) * rscale
        err.zero     <- sum(abs(rp2-0))
        err.pred.pos <- sum(abs(rp2 -  preds))
        err.pred.neg <- sum(abs(rp2 - -preds))
        err.pred     <- min(err.pred.pos, err.pred.neg)
        err.gain     <- err.zero - err.pred 

        errs.pred    <- c(errs.pred, err.pred)
        wins.pred    <- if(err.pred < err.zero) { c(wins.pred, 1) } else { c(wins.pred, 0) }
        errs.gain    <- c(errs.gain, err.gain)
    }
    cat("scale: ",     rscale, 
        "mean err: ",  mean(errs.pred), 
        "mean gain: ", mean(errs.gain), 
        "prob win: ",  mean(wins.pred), "\n")

}
