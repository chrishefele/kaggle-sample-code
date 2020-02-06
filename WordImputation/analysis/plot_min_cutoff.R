# plot tail of n-gram distributions to determine min number of instances needed
# such that all instances fit in memory (e.g. <40M ngrams for 8GB & python)

plot_tail <- function(fname) {
    cat("reading :", fname, "\n")
    n <- scan(fname)
    cat("plotting:", fname, "\n")
    mask <- 1:(length(n)/1000)
    mask <- mask * 1000
    plot(mask, n[mask], 
         main=paste("ngram file:", fname), 
         xlab="ngram rank", ylab="ngram count", 
         type="l", log="y", ylim=c(1,10))
}

# par(mrow=c(2,2))

pdf(file="plot_min_cutoff.pdf")
for(fname in c("n1", "n2", "n3", "n4")) {
    plot_tail(fname)
}