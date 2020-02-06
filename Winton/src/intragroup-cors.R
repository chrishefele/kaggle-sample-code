
library("reshape2")
library("dplyr")

PLOT.FILE  <- "intragroup-cors.pdf"
TRAIN.FILE <- "../data/train.RData"

HOUR1 <-   2:60    # columns of returns data 
HOUR2 <-  61:120
HOUR3 <- 121:180

GROUP.COL <- "Feature_7"

get.returns <- function(df, ret.nums) {
    # Extracts intra-day stock returns from a dataframe read from the .csv
    # Returned matrix has one column per stock, one row per intra-day minute
    ret.col.names <- paste("Ret", as.character(ret.nums), sep="_")
    returns.df            <- df[,ret.col.names]
    row.names(returns.df) <- df[,"Id"]
    #row.names(returns.df) <- paste("Id", df[,"Id"], sep="_")
    return( t(returns.df) )
}

sorted.cors <- function(ret.A, ret.B) {
    corAB  <- cor(ret.A, ret.B)
    melted <- melt(corAB, varnames=c("Id.A","Id.B"), value.name="corReturns")
    melted <- melted[(melted$Id.A != melted$Id.B), ]  # avoid cor=1 to same stock
    cors   <- melted$corReturns
    top.N  <- sort(cors, decreasing=TRUE)
    return(top.N)
}

do.cor.plot <- function(ret.A, ret.B, ret.baseline, ret.daily, tag) {
    plot(   sorted.cors(ret.A, ret.B),        
            type="l", log="x", main=tag, ylim=c(-1, 1) )
    #lines(sorted.cors(ret.A, ret.baseline), type="l", log="x", main=title, ylim=c(-1, 1) )
    lines(sorted.cors(ret.A, ret.baseline), lty=2)
    abline(h=0, lty=3, col="blue")

    cors.baseline <- sorted.cors(ret.A, ret.baseline)
    cors.group    <- sorted.cors(ret.A, ret.B)

    # histogram of baseline correlations
    hist(cors.baseline, xlim=c(-1,1), 40)
    abline(v=0, col="red", lwd=2)
    abline(v=median(cors.baseline), col="blue", lwd=2)

    # normalized hist of daily returns 
    ret.ratio <- ret.daily / colSums(abs(ret.A))
    # lim <- max(abs(ret.ratio))
    lim <- 2
    hist.title <- paste("NrmDlyRet",
                        "sd=",   round(sd(  ret.ratio), digits=4),
                        "median=", round(median(ret.ratio), digits=4)
                        )
    hist(ret.ratio, main=hist.title, xlim=c(-lim, lim), 20)
    abline(v=0, col="red", lwd=2)
    abline(v=median(ret.ratio), col="blue", lwd=2)

    # hist of group correlations
    hist(cors.group,    xlim=c(-1,1), 40)
    abline(v=0, col="red", lwd=2)
    abline(v=median(cors.group), col="blue", lwd=2)

    cat( "median.ret.ratio ", median(ret.ratio), 
        " median.cor.group ", median(cors.group), "\n")
}

main <- function() {

    pdf(file=PLOT.FILE) 
    par(mfrow=c(2,2))

    train <- readRDS(TRAIN.FILE)
    train[is.na(train)] <- 0 
    group.keys      <- train[,GROUP.COL]
    group.keys.uniq <- sort(unique(group.keys))

    groups.pct.lt0 <- c()
    cors.median <- c()
    cors.mins   <- c()
    cors.means  <- c()
    for(group.key in group.keys.uniq) {

        group.select <- group.key == group.keys
        random.select<- sample(1:nrow(train), sum(group.select))

        returns.A <- get.returns(train[group.select,],  HOUR2)
        returns.R <- get.returns(train[random.select,], HOUR2)

        cors <- sorted.cors(returns.A, returns.A)

        group.pct.lt0  <- 100 * sum(cors<0) / (sum(cors<0) + sum(cors>0))
        groups.pct.lt0 <- c(groups.pct.lt0, group.pct.lt0)
        cors.median    <- c(cors.median, median(cors))
        cors.mins      <- c(cors.mins, min(cors))
        cors.means     <- c(cors.means, mean(cors))

        cat("group: ", group.key, 
            " GT0: ", sum(cors > 0), 
            " LT0: ", sum(cors < 0), 
            " %LT0: ", group.pct.lt0, 
            " median: ", median(cors), 
            "\n"
        )
    }

    plot(   sort(cors.median, decreasing=TRUE), 
        type="l", 
        log="x", 
        main="Median of group correlations", 
        xlab="log group rank", 
        ylab="correlation" )
    hist(cors.median)

    plot(   sort(groups.pct.lt0, decreasing=FALSE), 
        type="l", 
        log="x", 
        main="%Correlations < 0", 
        xlab="log group rank", 
        ylab="%corr < 0" )
    hist(groups.pct.lt0)

    #for(group.key in group.keys.uniq[order(groups.pct.lt0)] ) {
    #for(group.key in group.keys.uniq[order(cors.mins)] ) {
    #for(group.key in group.keys.uniq[order(cors.means, decreasing=TRUE)] ) {
    for(group.key in group.keys.uniq[order(cors.median, decreasing=TRUE)] ) {

        group.select <- group.key == group.keys
        random.select<- sample(1:nrow(train), sum(group.select))

        returns.A <- get.returns(train[group.select,],  HOUR2)
        returns.R <- get.returns(train[random.select,], HOUR2)
        returns.plustwo <- train[group.select, "Ret_PlusTwo"]

        do.cor.plot(returns.A, returns.A, returns.R, returns.plustwo, paste("cors F7: ", group.key))
        cat("plotting group: ", group.key,"\n")
    }
}

main()

