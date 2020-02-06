
library(MASS)

cor.matrix <- rep(0.8, 100*100)
dim(cor.matrix) <- c(100,100)
diag(cor.matrix) <- 1

xlims <- c(-5,5)

par(mfrow=c(2,2))
for(i in 1:100) {

    cat(i,"\n")

    rands.uncor <- rnorm(100)
    hist(rands.uncor, xlim=xlims, main="Uncorrelated Rands")

    rands.cor   <- mvrnorm(n=1, mu=rep(0,100), Sigma=cor.matrix)
    hist(rands.cor, xlim=xlims, main="Correlated Rands")

}


