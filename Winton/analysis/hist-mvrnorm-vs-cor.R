
library(MASS)
pdf(file="hist-mvrnorm-vs-prob.pdf")

GROUP.COR <- 0.8   # HUGE impact on gains
DIMENSIONS <- 100
SAMPLES.PER.HIST <- 10000

cor.rnorm <- function(n.dim, n.samples, cor.const) {

    cor.matrix <- rep(cor.const, n.dim*n.dim)
    dim(cor.matrix) <- c(n.dim, n.dim)
    diag(cor.matrix) <- 1
    zero.means <- rep(0, n.dim)
    mvrnorm(n=n.samples, mu=zero.means, Sigma=cor.matrix)

}

for(group.cor in c(0:100)/100) {
    samples <- rowMeans( cor.rnorm(DIMENSIONS, SAMPLES.PER.HIST, group.cor) )
    title <- paste("Hist MeanGroupReturn", 
                   "group.cor=", group.cor, 
                   "sd=", round(sd(samples), digits=4)
             )
    cat(title,"\n")
    hist(samples, main=title, xlim=c(-3.5,3.5), 50)
}

