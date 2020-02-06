
library(quantreg)

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

train <- readRDS("../data/train.RData")

pdf(file="plot-train-timeseries-diffs.pdf")
par(mfrow=c(3,3))

#t.range <- c(2:180)
t.range <- c(2:120)
returns.cols <- paste("Ret", as.character(t.range), sep="_")
sort.key <- "Feature_7"
train <- train[order(train[,sort.key]),]

#for(row.num in 1:nrow(train)) {
for(row.num in 1:40000) {

    row.id         <- as.numeric(train[row.num, "Id"])
    sort.key.value <- as.numeric(train[row.num, sort.key])

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
        cat("  diff: ", diffs)
        #extreme <- max(abs(returns))
        sd.ratio <- sd(returns) / sd(returns.start) 
        cat(" plot-")
        plot(returns, type="l", ylim=c(-extreme, extreme), 
             main=paste( "row.id", as.character(row.id), 
                          "sort:",  sort.key.value, "diffs:", as.character(diffs) ),
             xlab=paste("sd.ratio:", sd.ratio)
        )
        cat("lowess-")
        lines(lowess(returns, f=1./5), col="blue")

        cat("acf-")
        acf( returns, main="ACF", ylim=c(-1,1))

        n <- length(returns)
        xt <- returns[1:n-1]
        yt <- returns[2:n]
        # NOTE jitter because rq seems to hang if too 
        # many x values are the same as y values
        xt <- jitter(xt, factor=0.1)
        yt <- jitter(yt, factor=0.1)

        cat("lm-")
        lm.model <- lm(yt~xt)
        slope <- round( coef(lm.model)[["xt"]], digits=3)
        cat("cor-")
        cor.xtyt <- round(cor(xt, yt), digits=3)
        cat("plot-")
        plot(   xt, yt, pch=".", 
                xlim=c(-extreme, extreme), ylim=c(-extreme, extreme), 
                xlab="returns(t-1)", ylab="returns(t)", 
                main=paste("slope:", slope, "cor:", cor.xtyt ))
        cat("abline.lm-")
        abline(lm(yt~xt), col="blue", lty=2)
        cat("abline.rq-")
        #if(row.num > 8715) {
        #    cat("\nyt:")
        #    print(yt)
        #    cat("\nxt:")
        #    print(xt)
        #}
        abline(rq(yt~xt), col="red",  lty=2)

        # lag.plot(   returns, layout=c(1,1), pch="." )
        cat("diff")
        returns <- diff(returns)
        cat("\n")
    }

}


