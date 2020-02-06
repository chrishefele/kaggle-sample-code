
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

#train <- readRDS("../data/test.RData")
train <- readRDS("../data/test_2.RData")

pdf(file="plot-test-timeseries.pdf")
par(mfrow=c(3,3))

t.range <- c(2:120)
returns.cols <- paste("Ret", as.character(t.range), sep="_")
sort.key <- "Feature_7"
train <- train[order(train[,sort.key]),]

for(row.num in 1:nrow(train)) {
#for(row.num in 1:40000) {

    row.id         <- as.numeric(train[row.num, "Id"])
    sort.key.value <- as.numeric(train[row.num, sort.key])
    feature.names  <- paste("Feature_", as.character(c(1,5,10,13,20)),sep="")
    feature.tags   <- paste(as.character(as.numeric(train[row.num, feature.names])), collapse='-')

    cat("plotting row: ", row.num,
        " row.id: ", row.id, 
        " sort.key.value: ", sort.key.value, "\n")

    returns <- as.numeric(train[row.num, returns.cols])
    returns[is.na(returns)] <- 0

    if(all(is.na(returns))) { 
        next 
    }

    norm.returns <- returns/sd(returns)
    plot(t.range, norm.returns, 
            type="l", 
            main=paste("row.id", as.character(row.id), 
                        "sort:", sort.key.value, 
                        paste(" F:",feature.tags,sep='')),
            ylim=c(-5,5))
    lines(lowess(t.range, norm.returns, f=1./5), col="blue")

    plot(t.range, cumsum(returns), type="l", main=paste("cumsum row", as.character(row.id)))
    lines(lowess(t.range, cumsum(returns)), col="blue")

    #plot(t.range, log10(abs(returns)),  type="l", main=paste("log10 abs return, row.id", as.character(row.id)))

    # plot(t.range, abs(returns),  type="l", main=paste("abs return, row.id", as.character(row.id)))
    #lines(lowess(t.range, abs(returns), f=1./5), col="blue")

    # plot(diff(returns),  type="l", main=paste("diff return, row.id", as.character(row.id)))
    # lines(lowess(diff(returns), f=1./5), col="blue")

    lag.plot(returns, layout=c(1,1), pch=".")
    #hist(returns ,  50, main="Histogram of Returns")
    lim <- max(abs(returns))
    hist(returns, 50, main="hist returns", xlim=c(-lim,lim))
    hist(log10(abs(returns)), 50, main=paste("log10 abs return, hist", as.character(row.id)))
    #hist(log10(abs(diff(returns))), 180, main=paste("log10 abs diff return, hist", as.character(row.id)))
    hist(sign(returns), main="hist sign returns")

    acf(    returns,  main="ACF  of Returns")
    acf(abs(returns), main="ACF  of Abs(Returns)")
    # acf(diff(returns), main="ACF  of diff(Returns)")

    acf(sign(returns), main="ACF sign returns")

    if(FALSE) {

        EPS <- 10^-4.5
        noise.mask <- (returns > -EPS) & (returns < EPS) 
        signal <- returns
        noise  <- returns
        signal[noise.mask] <- NA
        noise[!noise.mask] <- NA

        plot(t.range, signal, type="l", main="signal") 
        plot(t.range, noise , type="l", main="noise") 
        if(sum(!is.na(noise)) > 2) {
            acf(noise, na.action=na.pass, main="ACF of noise")
        } else {
            plot(c(0,1))
        }
    }

}


