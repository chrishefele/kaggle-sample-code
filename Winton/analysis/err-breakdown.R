pdf(file="err-breakdown.pdf")
TRAIN.FILE <- "../data/train.RData"

get.returns <- function(df, ret.nums) {
    # Extracts intra-day stock returns from a dataframe read from the .csv
    # Returned matrix has one column per stock, one row per intra-day minute
    ret.col.names <- paste("Ret", as.character(ret.nums), sep="_")
    returns.df            <- df[,ret.col.names]
    row.names(returns.df) <- df[,"Id"]
    return( t(returns.df) )
}

train <- readRDS(TRAIN.FILE)
train[is.na(train)] <- 0 

returns <- get.returns(train, c(2:120))
returns <- sample(c(returns), 100000)



hist(returns, 50)
plot(sort(returns), type="l", main="sorted returns")
plot(sort(abs(returns)), type="l", main="sorted abs returns")
plot(cumsum(sort(abs(returns))), type="l", main="cumsum sorted abs returns")


plot(ecdf(returns), main="ecdf returns"  ) 
plot(ecdf(abs(returns)), main="ecdf abs returns"  ) 




