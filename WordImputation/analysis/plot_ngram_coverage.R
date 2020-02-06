
plot_cumsum <- function(fname) { 
    counts <- scan(fname)
    pct <- cumsum(counts)/sum(counts)
    xi <- 2^(1:floor(log(length(pct))/log(2.)))
    plot(   xi, pct[xi], 
            type="l", 
            log="x", 
            xlim=c(1,1e9), 
            main=paste(fname,"normalized CUMULATIVE counts"),
            ylab="ngram coverage", 
            xlab="ngram lowest frequency rank (cumulative)"
    )
    cat('plotted: ', fname,'\n')
}

plot_counts <- function(fname) { 
    counts <- scan(fname)
    counts.norm <- counts/sum(counts)
    xi <- 2^(1:floor(log(length(counts.norm))/log(2.)))
    plot(   xi, counts.norm[xi], 
            type="l", 
            log="xy", 
            xlim=c(1,1e9), ylim=c(1e-9,1e-1),
            main=paste(fname, "ngram frequency "),
            ylab="ngram frequency", 
            xlab="ngram frequency rank"
    )
    cat('plotted: ', fname,'\n')
}

pdf(file="plot_ngram_coverage.pdf")

for(f in c("n1","n2","n3","n4")) {
    cat(paste("processing:",f,"\n"))
    plot_cumsum(f)
}

for(f in c("n1","n2","n3","n4")) {
    cat(paste("processing:",f,"\n"))
    plot_counts(f)
}
