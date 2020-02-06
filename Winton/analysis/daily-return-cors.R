

library("quantreg")

pdf(file="daily-return-cors.pdf")

train <- readRDS("../data/train.RData")

cols <- c("Ret_MinusTwo", "Ret_MinusOne", "Ret_PlusTwo", "Ret_PlusOne")

df <- train[,cols]
print(cor(df))

rm2  <- train$Ret_MinusTwo
rm1  <- train$Ret_MinusOne
rp1  <- train$Ret_PlusOne
rp2  <- train$Ret_PlusTwo


plotit <- function(x,y, tag) {
    lim <- 0.25
    plot(x, y, pch=".", xlim=c(-lim, lim), ylim=c(-lim, lim), main=tag)
    abline( rq(y~x), lty=2, col="red")
    abline( lm(y~x), lty=2, col="blue")
}

plotit(rm2, rm1, "rm2->rm1")
plotit(rm2, rp1, "rm2->rp1")
plotit(rm2, rp2, "rm2->rp2")
plotit(rm1, rp1, "rm1->rp1")
plotit(rm1, rp2, "rm1->rp2")
plotit(rp1, rp2, "rp1->rp2")

errs <- function(x,y, tag) {

    errs.lm   <- sum(abs(y - predict(lm(y~x))))
    errs.rq   <- sum(abs(y - predict(rq(y~x))))
    errs.medx <- sum(abs(y - median(x)))
    errs.medy <- sum(abs(y - median(y)))
    errs.zero <- sum(abs(y - 0))

    cat(tag, " errs.lm  : ", errs.lm/errs.zero,"\n")
    cat(tag, " errs.rq  : ", errs.rq/errs.zero,"\n")
    cat(tag, " errs.medx: ", errs.medx/errs.zero,"\n")
    cat(tag, " errs.medy: ", errs.medy/errs.zero,"\n")
    cat(tag, " errs.zero: ", errs.zero/errs.zero,"\n")
    cat("\n")

}

errs(rm2, rm1, "rm2->rm1")
errs(rm2, rp1, "rm2->rp1")
errs(rm2, rp2, "rm2->rp2")
errs(rm1, rp1, "rm1->rp1")
errs(rm1, rp2, "rm1->rp2")
errs(rp1, rp2, "rp1->rp2")



