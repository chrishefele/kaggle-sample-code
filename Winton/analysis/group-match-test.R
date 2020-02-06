# The purpose of this script is to try to find time-aligned gruops of stocks
# which could be used for "prediction" (via leakage of info from future prices)
# Stocks are grouped using Feature_7 (which has some time component, via exploratory
# data analysis).  Then the returns of all stocks in a group are correlated with 
# all other stocks, then the results rolled up per group (the results are 
# average correlation in the group to all other stocks in another group).
# The results are also plotted. 
#
# Chris Hefele, 11/9/2015
#
# Updated Dec 2015 for new test set & to clamp spikes

library("reshape2")
library("dplyr")

PLOT.FILE  <- "group-match-test.pdf"
TEST.FILE  <- "../data/test_2.RData"
CLAMP.SD   <- 3

HOUR1 <-   2:60    # columns of returns data 
HOUR2 <-  61:120
HOUR12<- c(HOUR1, HOUR2)

GROUP.COL <- "Feature_7"

clamp <- function(x) {
    x <- as.numeric(x)
    x.trim <- sort(x)[2:(length(x)-1)] # remove largest & smallest value
    lim <- CLAMP.SD * sd(x.trim)
    x[ x >  lim] <-  lim
    x[ x < -lim] <- -lim
    return(x)
}

clamp.cols <- function(m) {
    apply(m, 2, clamp)
}


get.returns <- function(df, ret.nums) {
    # Extracts intra-day stock returns from a dataframe read from the .csv
    # Returned matrix has one column per stock, one row per intra-day minute
    ret.col.names <- paste("Ret", as.character(ret.nums), sep="_")
    returns.df            <- df[,ret.col.names]
    row.names(returns.df) <- df[,"Id"]
    #row.names(returns.df) <- paste("Id", df[,"Id"], sep="_")
    #return( clamp.cols(t(returns.df))) # use spearman rank cor below instead
    return( t(returns.df) )
}

main <- function() {

    pdf(file=PLOT.FILE) 
    par(mfrow=c(2,2))

    train <- readRDS(TEST.FILE)
    train[is.na(train)] <- 0 
    group.keys <- train[,GROUP.COL]

    Id.A.group <- data.frame( Id.A=train$Id, group.A=train[,GROUP.COL] )
    Id.B.group <- data.frame( Id.B=train$Id, group.B=train[,GROUP.COL] )

    returns.A <- get.returns(train, HOUR12)

    for(group.key in sort(unique(group.keys))) {

        cat("processing group key: ", group.key, "\n")

        group.select <- group.key == group.keys
        returns.B <- get.returns(train[group.select,], HOUR12)

        #corAB     <- cor(returns.A, returns.B)
        # use spearman rank correlation to decrease the impact of spikes
        corAB     <- cor(returns.A, returns.B, method="spearman") 

        melted <- melt(corAB, varnames=c("Id.A","Id.B"), value.name="corReturns")
        # melted <- melted[(melted$Id.A != melted$Id.B), ]  # avoid cor=1 to same stock
        melted <- left_join(melted, Id.A.group, by="Id.A")
        melted <- left_join(melted, Id.B.group, by="Id.B")
        grouped <- group_by(melted, group.A, group.B) # should be group.A and group.B
        group.summary <- summarise( grouped
                                    ,mean=mean(corReturns)
                                    ,sd=sd(corReturns)
                                    ,median=median(corReturns)
                                    ,iqr=IQR(corReturns)
                                    ,max=max(corReturns)
                                    ,min=min(corReturns)
                                  )

        plot(   group.summary$mean, 
                type="l" ,
                main=paste("mean F7 Group:", group.key),
                ylim=c(-0.5,0.5),
                ylab="meanGroupRankCor")
        abline(h= 1*sd(group.summary$mean), lty=3, col="blue")
        abline(h= 2*sd(group.summary$mean), lty=3, col="blue")
        abline(h= 3*sd(group.summary$mean), lty=3, col="blue")
        abline(h=-1*sd(group.summary$mean), lty=3, col="red")
        abline(h=-2*sd(group.summary$mean), lty=3, col="red")
        abline(h=-3*sd(group.summary$mean), lty=3, col="red")

        plot(   sort(group.summary$mean), 
                type="l" ,
                main=paste("mean F7 Group:", group.key) ,
                ylim=c(-1,1),
                ylab="meanGroupRankCor")
        lines( sort(group.summary$max), type="l", col="green" )
        lines( sort(group.summary$min), type="l", col="red"   )
        abline(h= 1*sd(group.summary$mean), lty=3, col="blue")
        abline(h= 2*sd(group.summary$mean), lty=3, col="blue")
        abline(h= 3*sd(group.summary$mean), lty=3, col="blue")
        abline(h=-1*sd(group.summary$mean), lty=3, col="red")
        abline(h=-2*sd(group.summary$mean), lty=3, col="red")
        abline(h=-3*sd(group.summary$mean), lty=3, col="red")

        norm.top.ten <- sort(group.summary$mean, decreasing=TRUE)[1:10] / sd(group.summary$mean)
        plot(norm.top.ten,  type="b" ,main=paste("mean/sd F7 Group:",     group.key) )

        norm.top.ten <- sort(abs(group.summary$mean), decreasing=TRUE)[1:10] / sd(group.summary$mean)
        plot(norm.top.ten,  type="b" ,main=paste("abs mean/sd F7 Group:",     group.key) )
        # hist(group.summary$mean)
    }
}

main()

