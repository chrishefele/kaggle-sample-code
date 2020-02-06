
NONZEROS <- c(2,4,8,16,32,64, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 40000)

train <- readRDS("../data/train.RData")
train[is.na(train)] <- 0

wt  <- train$Weight_Daily
rp2 <- train$Ret_PlusTwo
rm2 <- train$Ret_MinusTwo

for(nonzeros in NONZEROS) {

    err.min <- 999999999

    signs <- rep(0, length(rm2))
    n.nonneg <- sample(1:length(rm2), NONZEROS)
    n.pos    <- sample( n.nonneg,     NONZEROS/2)
    n.neg    <- sample(-n.nonneg,     NONZEROS/2)
    signs[n.pos] <-  1
    signs[n.neg] <- -1

    for(loop in 1:1000) {

        preds <- rm2 * sample(signs)
        err.zero <- sum(abs(rp2-0))
        err.pred <- sum(abs(rp2 - preds))
        err.min  <- min(err.min, err.pred)
        err.min.gain <- err.zero - err.min

        if(FALSE) {
            cat("loop: ", loop, 
                " err.zero: ", err.zero, 
                " err.pred: ", err.pred, 
                "err.min: ", err.min, 
                "err.min.gain :", err.min.gain, "\n")
        }

    }

    cat("nonzeros: ", nonzeros, " err.min.gain :", err.min.gain, "\n")
}

