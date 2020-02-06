
library("quantreg")
pdf(file="big-rq.pdf")

train <- readRDS("../data/train.RData")

ret120 <- train[,"Ret_120"]
ret121 <- train[,"Ret_121"]
# hist(ret120)

ret.t           <- ret121
ret.t.minus1    <- ret120

model <- rq(ret.t ~ ret.t.minus1)

lim <- 0.02
plot(ret.t.minus1, ret.t, pch=".", xlim=c(-lim,lim), ylim=c(-lim,lim))
abline(model, col="red", lty=2)

plot(cumsum(sort(abs(ret120))), type="l")
plot(cumsum(sort(abs(ret120-ret121))), type="l")

hist(log10(abs(ret120)), 100)
hist(log10(abs(ret120-ret121)), 100)

err.zero        <- sum(abs(ret121 - 0))
err.last        <- sum(abs(ret121 -  ret120))
err.neglast     <- sum(abs(ret121 - -ret120))
err.rq          <- sum(abs(ret121 - predict(model)))
err.median120   <- sum(abs(ret121 - median(ret120)))
err.median121   <- sum(abs(ret121 - median(ret121)))

print(median(ret120))
print(median(ret121))

cat("err.zero     : ", err.zero, "\n")
cat("err.last     : ", err.last, "\n")
cat("err.neglast  : ", err.neglast, "\n")
cat("err.rq       : ", err.rq, "\n")
cat("err.median120: ", err.median120, "\n")
cat("err.median121: ", err.median121, "\n")


