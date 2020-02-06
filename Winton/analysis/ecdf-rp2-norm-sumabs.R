

SUMABS.TO.RET <- 0.19

pdf(file="ecdf-rp2-norm-sumabs.pdf")

train <- readRDS("../data/train.RData")
train[is.na(train)] <- 0 

ret.cols <- paste("Ret", 2:120, sep="_")
ret <- train[,ret.cols]

ret.sumabs <- rowSums(abs(ret))

rp2 <- train[,"Ret_PlusTwo"]

norm.abs.rp2 <- abs(rp2) / (ret.sumabs * SUMABS.TO.RET)

print(summary(norm.abs.rp2))

e <- ecdf(norm.abs.rp2)

plot(e)
plot(e, xlim=c(0, 10))
plot(e, xlim=c(0, 5))
plot(e, xlim=c(0, 2))
plot(e, xlim=c(0, 1))
plot(e, xlim=c(0, 0.5))
plot(e, xlim=c(0, 0.2))
 
print(e)





