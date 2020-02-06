
library(MASS)
pdf(file="scale-medianabs-examples.pdf")
par(mfrow=c(3,2))

GROUP.COR  <- 0.8   # HUGE impact on gains
DIMENSIONS <- 100


cor.rnorm <- function(n, cor.const) {

    cor.matrix <- rep(cor.const, n*n)
    dim(cor.matrix) <- c(n, n)
    diag(cor.matrix) <- 1
    zero.means <- rep(0, n)
    mvrnorm(n=1, mu=zero.means, Sigma=cor.matrix)

}

optimal.scale <- function(scalings, errs) {
    N <- length(scalings)
    scale.left  <- scalings[1]
    err.left    <- errs[1]
    scale.right <- scalings[N]
    err.right   <- errs[N]
    if(err.left > err.right) {
        xopt <- -(err.left - err.right)/2 * (scale.left / err.left)
    } else { 
        xopt <- -(err.right - err.left)/2 * (scale.right / err.right)
    }
    return(xopt)
}

plot.plots <- function(scalings, errs.median, tag) {

    plot(scalings,  errs.median, type="l", col="red", main=tag)
    abline(h=0, col="blue", lty=2)
    abline(v=0, col="blue", lty=2)
    xopt <- optimal.scale(scalings, errs.median)
    abline(v=xopt, col="green", lty=1)

    plot(scalings[-1], diff(errs.median), type="l", col="blue", main="derivative")
}

main <- function(group.cor) {

    for(loop in c(1:1000)) {
        cat("plot: ", loop, "\n")

        target <- cor.rnorm(DIMENSIONS, group.cor)
        guess  <- cor.rnorm(DIMENSIONS, group.cor)
        guess  <- guess * sign(median(guess)) 
        guess.median <- 0*guess + median(abs(guess))
        #guess.median <- 0*guess + mean(abs(guess))

        err.median <- function(scaling) {
            sum(abs(scaling*guess.median - target)) / sum(abs(0 - target)) - 1.0
        }

        N <- 100
        for(scaling in c(1,3,9)) {
            scalings <- c((-scaling*N):(scaling*N))/N
            errs.median <- sapply(scalings, err.median)
            plot.plots(scalings, errs.median, paste("errs vs scaling, cor=", group.cor) )
        }

    }

}

main(GROUP.COR)
