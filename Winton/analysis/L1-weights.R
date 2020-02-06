library(MASS)
pdf(file="L1-weights.pdf")

GROUP.COR <- 0.8   # HUGE impact on gains
DIMENSIONS <- 100


cor.rnorm <- function(n, cor.const) {

    cor.matrix <- rep(cor.const, n*n)
    dim(cor.matrix) <- c(n, n)
    diag(cor.matrix) <- 1
    zero.means <- rep(0, n)
    mvrnorm(n=1, mu=zero.means, Sigma=cor.matrix)

}

plot.plots <- function(scalings, errs.L1, errs.L2, tag) {
    lim <- max(abs(errs.L1))
    plot(scalings,  errs.L1, 
         type="l", 
         col="red", 
         ylim=c(-lim, lim), 
         main=tag
    )
    #plot(scalings,  errs.L1, type="l", col="red")
    lines(scalings, errs.L2, type="l", col="blue")
    abline(h=0, col="green", lty=2)
}

main <- function(group.cor) {

    min.errs.L1 <- c()
    errs.L1.vecsum <- 0
    errs.L2.vecsum <- 0

    for(loop in c(1:1000)) {

        # cat(loop, " ")

        target <- cor.rnorm(DIMENSIONS, group.cor)
        guess  <- cor.rnorm(DIMENSIONS, group.cor)
        guess.L1 <- guess * sum(abs(target))    / sum(abs(guess)) 
        guess.L2 <- guess * sqrt(sum(target^2)) / sqrt(sum(guess^2))

        err.L1 <- function(scaling) {
            sum(abs(scaling*guess.L1 - target)) / sum(abs(0 - target)) - 1.0
        }

        err.L2 <- function(scaling) {
            rse <- sqrt(sum((scaling*guess.L1 - target)^2))
            target.norm <- sqrt(sum(target^2))
            return(rse/target.norm - 1)
        }

        N <- 100
        scalings <- c((-1.5*N):(1.5*N))/N
        errs.L1 <- sapply(scalings, err.L1)
        errs.L2 <- sapply(scalings, err.L2)

        #plot.plots(scalings, errs.L1, errs.L2, "errs vs scaling")

        min.errs.L1 <- c(min.errs.L1, min(errs.L1))

        if(errs.L1[1] > errs.L1[length(errs.L1)]) {
            errs.L1.vecsum <- errs.L1.vecsum + errs.L1
            errs.L2.vecsum <- errs.L2.vecsum + errs.L2
        }

    }

    cat("group.cor: ", group.cor, 
        " median L1.err: ", median(min.errs.L1),
        " mean L1.err: ", mean(  min.errs.L1),
        "\n"
    )

    #hist(min.errs.L1)
    plot.plots(scalings, errs.L1.vecsum, errs.L2.vecsum, 
               paste("tot errs vs scaling, group.cor=", group.cor))

}

for(g.cor in c(0:100)/100) {
    main(g.cor)
}

