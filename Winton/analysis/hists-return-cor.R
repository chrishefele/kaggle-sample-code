
pdf(file="hists-return-cor.pdf")

SAMPLE.NSTOCKS  <- 3000
HOUR.1.COLS     <-  2:60
HOUR.2.COLS     <- 62:120

train <- readRDS("../data/train.RData")
train[is.na(train)] <- 0 
row.select      <- sample(1:nrow(train), SAMPLE.NSTOCKS)
train <- train[row.select,] 

get.returns <- function(df, ret.nums) {
    # Extracts intra-day stock returns from a dataframe read from the .csv
    # Returned matrix has one column per stock, one row per intra-day minute
    col.names <- paste("Ret", as.character(ret.nums), sep="_")
    returns.df <- df[,col.names]
    ids        <- df[,"Id"] 
    row.names(returns.df) <- paste("Id", ids, sep="_")
    return( t(returns.df) ) 
}

shuffle <- function(m) {
    # This function shuffles the values in each matrix column independently.
    # Assuming an input matrix of returns (one col/stock, one row/minute),
    # this permutes the minute-by-minute returns for each stock
    m.shuf <- apply(m, 2, sample) 
    rownames(m.shuf) <- rownames(m)
    return(m.shuf)
}

ret.H1          <- get.returns(train, HOUR.1.COLS)
ret.H2          <- get.returns(train, HOUR.2.COLS)
ret.H1.shuf     <- shuffle(ret.H1)

cor1.tmp <- cor(ret.H1, ret.H1)
diag(cor1.tmp) <- 0
cor1 <- c(cor1.tmp)
cor2 <- c(cor(ret.H1, ret.H1.shuf))
cor3 <- c(cor(ret.H1, ret.H2))

hist(cor1, 50, xlim=c(-1,1))
hist(cor2, 50, xlim=c(-1,1))
hist(cor3, 50, xlim=c(-1,1))

xlim <- c(0.3,1)
ylim <- c(0.995, 1)
# plot(ecdf(x), xlim=c(1,4), ylim=c(0.6,1), pch=".", col="blue", add=TRUE)
plot(ecdf(sample(cor1,10000)), xlim=xlim, ylim=ylim, pch=".", col="blue", add=FALSE)
plot(ecdf(sample(cor2,10000)), xlim=xlim, ylim=ylim, pch=".", col="red", add=TRUE)
plot(ecdf(sample(cor3,10000)), xlim=xlim, ylim=ylim, pch=".", col="green", add=TRUE)

