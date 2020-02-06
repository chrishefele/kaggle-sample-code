
library(MASS)
library(quantreg)

N.MINUTES         <- 100
N.TRIALS          <- 10000
GROUP.CORS        <- c(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99)

cor.rnorm <- function(n.dim, n.samples, cor.const) {
    # returns a matrix with one n.dim sample per row, n.samples rows
    cor.matrix <- rep(cor.const, n.dim*n.dim)
    dim(cor.matrix) <- c(n.dim, n.dim)
    diag(cor.matrix) <- 1
    zero.means <- rep(0, n.dim)
    mvrnorm(n=n.samples, mu=zero.means, Sigma=cor.matrix)
}


# rets <- t(cor.rnorm(N.GROUP.STOCKS, N.TRIALS, group.cor))
rets <- rnorm(N.TRIALS * N.MINUTES)
dim(rets) <- c(N.TRIALS, N.MINUTES)

x <- rowMeans(abs(rets))
y <- abs(rowMeans(rets))
model <- rq(y ~ 0 + x)
print(model)

pdf()
hist(y/x, 100)
hist(log10(y/x), 100)

