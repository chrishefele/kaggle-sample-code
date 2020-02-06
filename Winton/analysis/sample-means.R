
library(MASS)

pdf(file="sample-means.pdf")

cor.rnorm <- function(n.dim, n.samples, cor.const) {

    cor.matrix <- rep(cor.const, n.dim*n.dim)
    dim(cor.matrix) <- c(n.dim, n.dim)
    diag(cor.matrix) <- 1
    zero.means <- rep(0, n.dim)
    mvrnorm(n=n.samples, mu=zero.means, Sigma=cor.matrix)
}

N.dim  <- 100
trials <- 1000

group.cors <- c(0:100) / 100

for(group.cor in group.cors) {

    cat("processing cor: ", group.cor, "\n")

    x <- cor.rnorm(N.dim, trials, group.cor)
    sample.cols <- sample(1:N.dim, N.dim/3)
    public.means <- rowMeans(x[, sample.cols])
    private.means  <- rowMeans(x[,-sample.cols])

    # lim <- max(max(abs(train.means)), max(abs(test.means)))
    lim <- 3
    plot(   public.means, private.means, 
            pch=".", 
            xlim=c(-lim, lim), ylim=c(-lim,lim),
            main=paste("private mean vs public mean, cor=", group.cor)
    )
    abline(h=0, lty=2)
    abline(v=0, lty=2)

}
