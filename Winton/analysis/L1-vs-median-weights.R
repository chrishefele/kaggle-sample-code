
library(MASS)
pdf(file="L1-vs-median-weights.pdf")

GROUP.COR <- 0.8   # HUGE impact on gains
DIMENSIONS <- 100


cor.rnorm <- function(n, cor.const) {

    cor.matrix <- rep(cor.const, n*n)
    dim(cor.matrix) <- c(n, n)
    diag(cor.matrix) <- 1
    zero.means <- rep(0, n)
    mvrnorm(n=1, mu=zero.means, Sigma=cor.matrix)

}

plot.plots <- function(scalings, errs.L1, errs.median, tag) {
    # lim <- max(abs(errs.L1)) # autoscale
    lim <- 1000
    plot(scalings,  errs.L1, 
         type="l", 
         col="red", 
         ylim=c(-lim, lim), 
         main=tag
    )
    lines(scalings, errs.median, type="l", col="blue", lty=6)
    legend("topright", 
            legend=c("Scaled Random Guess", "Scaled Median(const) Guess"), 
            col=c("red","blue") , lty=c(1,6))
    abline(h=0, col="green", lty=2)
    abline(v=0, col="green", lty=2)
}

main <- function(group.cor) {

    min.errs.L1 <- c()
    errs.L1.vecsum <- 0
    errs.median.vecsum <- 0

    for(loop in c(1:1000)) {

        # cat(loop, " ")

        target <- cor.rnorm(DIMENSIONS, group.cor)
        guess  <- cor.rnorm(DIMENSIONS, group.cor)
        guess  <- guess * sign(median(guess))
        #guess.L1     <- guess * sum(abs(target))    / sum(abs(guess)) 
        #guess.median <- 0*guess.L1 + median(guess.L1)
        guess.L1     <-   guess 
        guess.median <- 0*guess + median(abs(guess))

        err.L1 <- function(scaling) {
            sum(abs(scaling*guess.L1 - target)) / sum(abs(0 - target)) - 1.0
        }

        err.median <- function(scaling) {
            sum(abs(scaling*guess.median - target)) / sum(abs(0 - target)) - 1.0
        }

        N <- 100
        scalings <- c((-1.5*N):(1.5*N))/N
        errs.L1     <- sapply(scalings, err.L1)
        errs.median <- sapply(scalings, err.median)

        # plot.plots(scalings, errs.L1, errs.median, "errs vs scaling")

        min.errs.L1 <- c(min.errs.L1, min(errs.L1))

        if(errs.L1[1]     > errs.L1[    length(errs.L1)]) {
            errs.L1.vecsum         <- errs.L1.vecsum     + errs.L1
        }
        if(errs.median[1] > errs.median[length(errs.median)]) {
            errs.median.vecsum     <- errs.median.vecsum + errs.median
        }

    }

    cat("group.cor: ", group.cor, 
        " median L1.err: ", median(min.errs.L1),
        " mean L1.err: ",   mean(min.errs.L1),
        "\n"
    )

    #hist(min.errs.L1)
    plot.plots(scalings, errs.L1.vecsum, errs.median.vecsum, 
               paste("tot errs vs scaling, group.cor=", group.cor))

}

for(g.cor in c(0:20)/20) {
    main(g.cor)
}

