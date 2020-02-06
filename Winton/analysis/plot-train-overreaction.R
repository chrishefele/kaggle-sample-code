
train <- readRDS("../data/train.RData")
train[is.na(train)] <- MIN.RETURN <- 1E-7

pdf(file="plot-train-overreaction.pdf")
#par(mfrow=c(2,2))

myplot <- function(x, y, tag) {
    lim <- max(c(abs(x), abs(y))) * 0.6 
    plot(x, y, 
         pch=".", 
         xlim=c(-lim, lim), ylim=c(-lim,lim),
         main=tag
    )
    lines( c(-lim, -lim), c(lim, lim), col="red", lty=2) # diagonal
    abline(coef=c(0,1), col="red", lty=2)
    lines(lowess(x, y, f=1./5), col="blue")
    abline(v=median(x), col="red", lty=2)
}

norms <- rowSums( abs(train[, paste("Ret", 2:120, sep="_")]))

rt0 <- train$Ret_PlusOne / norms
rt1 <- train$Ret_PlusTwo / norms 

sample.mask <- runif(length(rt0)) < abs(rt0)
rt0.samp <- rt0[sample.mask]
rt1.samp <- rt1[sample.mask]

myplot(rt0,             rt1,            "RP2 v RP1")
myplot(rt0.samp,        rt1.samp,       "RP2 v RP1 sampled")

myplot(abs(rt0),        abs(rt1),       "abs(RP2 v RP1)")
myplot(abs(rt0.samp),   abs(rt1.samp),  "abs(RP2 v RP1) sampled")


myplot(log10(abs(rt0)),        log10(abs(rt1)),       "log10(abs(RP2 v RP1))")
myplot(log10(abs(rt0.samp)),   log10(abs(rt1.samp)),  "log10(abs(RP2 v RP1)) sampled")

myplot(log10(abs(rt0))     *sign(rt0),        log10(abs(rt1))     *sign(rt1),       "sgn*log10(abs(RP2 v RP1))")
myplot(log10(abs(rt0.samp))*sign(rt0.samp),   log10(abs(rt1.samp))*sign(rt1.samp),  "sgn*log10(abs(RP2 v RP1)) sampled")


par(mfrow=c(1,1))
myplot(log10(abs(rt0)),        log10(abs(rt1)),       "log10(abs(RP2 v RP1))")

