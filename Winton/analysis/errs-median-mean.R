
csv.data <- readRDS("../data/train.RData")

for(end.col in c(121:180)) {

    # train.cols  <- paste("Ret_", as.character(c(  2:120)), sep="")
    train.cols  <- paste("Ret_", as.character(c(  2:120)),     sep="")
    test.cols   <- paste("Ret_", as.character(c(121:end.col)), sep="")

    train.returns   <- as.matrix(csv.data[,train.cols])
    test.returns    <- as.matrix(csv.data[,test.cols])
    weights         <- csv.data[,"Weight_Intraday"]

    train.returns[is.na(train.returns)] <- 0

    median.rmna <- function(r) median(r, na.rm=TRUE)
    mean.rmna   <- function(r) mean(  r, na.rm=TRUE)
    zero.rmna   <- function(r) 0

    noise.median <- function(r) {
        EPS <- 10^-4.5
        noise.mask <- (r > -EPS) & (r < EPS) 
        if(any(noise.mask, na.rm=TRUE)) {
            return(median(r[noise.mask], na.rm=TRUE))
        } else {
            return(0)
        }
    }


    medians <- apply(train.returns, 1, median.rmna)  
    means   <- apply(train.returns, 1, mean.rmna)   
    zeros   <- apply(train.returns, 1, zero.rmna)
    noise.medians <- -apply(train.returns, 1, noise.median)

    mad.medians  <- mean( weights * rowMeans(abs(test.returns- medians)))
    mad.means    <- mean( weights * rowMeans(abs(test.returns - means  )))
    mad.zeros    <- mean( weights * rowMeans(abs(test.returns - zeros  ))) 
    # mad.noise    <- mean( weights * rowMeans(abs(test.returns - noise.medians))) 

    cat("Test end_col: ", end.col)
    cat(" MAD_median: ",  mad.medians)
    cat(" MAD_mean: ",    mad.means)
    cat(" MAD_zero: ",    mad.zeros)
    # cat(" MAD_noise : ",    mad.noise)
    cat(" median-zero : ", mad.medians - mad.zeros, "\n")

}

