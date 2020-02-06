
# twoguess optimal partitioning

pdf(file="twoguess-opt-partition.pdf")

GROUPS           <- 1000
PARTITION.TRIALS <- 2000

rand.matrix <- function(r,c) {
    randm <- rnorm(r*c)
    dim(randm) <- c(r,c)
    return(randm)
}

row.medians <- function(m) {
    apply(m, 1, median)
}

scale.cols <- function(mtrx, col.scales.vec) {
   t( t(mtrx) * col.scales.vec)  
}



errs <- c()
for(split in 1:(GROUPS-1) ) {
    

    r1 <- rand.matrix(PARTITION.TRIALS,          split)
    r2 <- rand.matrix(PARTITION.TRIALS, GROUPS - split)

    # make random variables with decreasing magnitudes 
    scales <- 1. - (c(1:GROUPS) / GROUPS)
    r1 <- scale.cols(r1, scales[ 1         : split ])
    r2 <- scale.cols(r2, scales[ (split+1) : GROUPS])

    preds1 <- as.vector(row.medians(r1))
    preds2 <- 0

    err1 <- sum(abs(r1 - preds1))
    err2 <- sum(abs(r2 - preds2))
    err.zero <- sum(abs(r1-0)) + sum(abs(r2-0))

    err  <- err1 + err2 
    err.vs.zero <- 1 - err / err.zero 
    errs <- c(errs, err)
    cat("split: ", split, " err: ", err, " err.vs.zero (gain): ", err.vs.zero, "\n")
}

print(errs)
print(1-errs/max(errs))

plot(  errs,           xlab="split", ylab="err", main="errs vs split")
plot(1-errs/max(errs), xlab="split", ylab="err", main="relative errs vs split")

plot(  errs,           xlab="split", ylab="err", main="errs vs split",          log="x")
plot(1-errs/max(errs), xlab="split", ylab="err", main="relative errs vs split", log="x")

