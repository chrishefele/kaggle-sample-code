
library(quantreg)

#GROUPS.OF.INTEREST <- c(12177, 37959, 38778, 80097, 91350, 95190, 
#                        26, 5174, 5540, 11260, 11452, 22658, 29709, 
#                        31554, 44896, 46537, 95190)

GROUPS.OF.INTEREST <- c(2783, 5051, 7141, 60622,66845, 75916, 98984) 

#------------------- 

gplot.xy <- function(x.in,y.in, title, x.name, y.name) {
    ggraph <-   ggplot(df.xy, aes(x=x.in,y=y.in)) +
                ggtitle(title) +
                labs(x=x.name, y=y.name) +
                # coord_cartesian(xlim=c(x.lo, x.hi), ylim=c(y.lo, y.hi))
                theme_bw()  + 
                geom_line() + 
                geom_smooth(method="loess") #option: size=2
    print(ggraph)
}

#------------------- 

train <- readRDS("../data/test_2.RData")

pdf(file="plot-test-timeseries-diffs.pdf")
par(mfrow=c(3,3))

t.range <- c(2:120)
returns.cols <- paste("Ret", as.character(t.range), sep="_")
sort.key <- "Feature_7"
train <- train[order(train[,sort.key]),]

for(row.num in 1:nrow(train)) {
#for(row.num in 1:40000) {

    row.id         <- as.numeric(train[row.num, "Id"])
    sort.key.value <- as.numeric(train[row.num, sort.key])
    
    if(!(sort.key.value %in% GROUPS.OF.INTEREST)) {
        next
    }

    cat("plotting row: ", row.num, " row.id: ", row.id, "\n")

    returns <- as.numeric(train[row.num, returns.cols])
    returns[is.na(returns)] <- 0
    if(all(is.na(returns))) { 
        next 
    }

    returns.start <- returns
    returns <- cumsum(returns)
    extreme <- max(abs(returns))

    for(diffs in c(-1, 0, 1)) {
        #extreme <- max(abs(returns))
        sd.ratio <- sd(returns) / sd(returns.start) 
        plot(returns, type="l", ylim=c(-extreme, extreme), 
             main=paste( "row.id", as.character(row.id), 
                          "sort:",  sort.key.value, "diffs:", as.character(diffs) ),
             xlab=paste("sd.ratio:", sd.ratio)
        )
        lines(lowess(returns, f=1./5), col="blue")

        acf( returns, main="ACF", ylim=c(-1,1))

        n <- length(returns)
        xt <- returns[1:n-1]
        yt <- returns[2:n]
        lm.model <- lm(yt~xt)
        slope <- round( coef(lm.model)[["xt"]], digits=3)
        cor.xtyt <- round(cor(xt, yt), digits=3)
        plot(   xt, yt, pch=".", 
                xlim=c(-extreme, extreme), ylim=c(-extreme, extreme), 
                xlab="returns(t-1)", ylab="returns(t)", 
                main=paste("slope:", slope, "cor:", cor.xtyt ))
        abline(lm(yt~xt), col="blue", lty=2)
        abline(rq(yt~xt), col="red",  lty=2)

        # lag.plot(   returns, layout=c(1,1), pch="." )
        returns <- diff(returns)
    }

}


