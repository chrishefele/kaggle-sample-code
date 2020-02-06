
cat("reading trigram counts and unigram ranks\n")
v <- read.csv("vocab_size.csv") # columns: count, maxrank
cat(nrow(v)," rows read\n")

pdf(file="vocab_size.pdf")

vocab_sizes <- 2 ^ c(7:22)
for(vocab_size in vocab_sizes) {

    cat("vocab size:", vocab_size)
    tag <- paste("Vocabulary size:", as.character(vocab_size))

    mask <- (v$maxrank < vocab_size)*1
    y <- cumsum( mask*v$count ) / cumsum(v$count)
    cat("  trigram coverage:", y[length(y)] ,"\n")

    BASE <- 1.1
    xi <- BASE ^ (1:floor(log(length(y))/log(BASE)))
    plot(   xi, y[xi], 
            ylim=c(0,1), ylab="trigram coverage", 
            xlab="cumulative trigrams (in popularity order)",
            type="l", log="x", main=tag )

}

