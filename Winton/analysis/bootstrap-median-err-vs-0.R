
N <- 1000


test2 <- readRDS("../data/test_2.RData")
rm2 <- test2$Ret_MinusTwo

err.diffs <- c()

for(i in 1:N) {

    s <- sample(rm2, replace=TRUE)
    err.zero   <- sum(abs(s-0))
    err.median <- sum(abs(s-median(s)))
    err.diff   <- (err.zero - err.median)
    cat(i, " err.zero: ", err.zero, "err.median: ", err.median, "err.diff: ", err.diff, "\n")
    err.diffs <- c(err.diffs, err.diff)

}

hist(err.diffs, 50)

