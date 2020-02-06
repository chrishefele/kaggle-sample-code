library(zoo)

LAGS <- as.integer( c(4,8,16,32,64,128,256,512) )

train <- read.csv("/home/chefele/Ford/download/fordTrain.csv")
pdf(file="lagplot.rolling.abs-x-mean.pdf")

lagcol <- function(the.col, the.lag) {     # timelag a vector of data
    end.index <- length(the.col) - the.lag
    padding <- rep( the.col[1], the.lag ) 
    return(  c( padding, the.col[1:end.index] ) )
}

meanfreq <- function(x) {
    full.pwr.spectrum <- Mod( fft(x) )^2
    first.half.freqs <- 1:(length(full.pwr.spectrum)/2)
    pwr.spectrum <- full.pwr.spectrum[ first.half.freqs ]  
    mean.freq <- sum( pwr.spectrum*(first.half.freqs-1) ) / sum( pwr.spectrum ) 
    return( mean.freq ) 
}

xminusmean <- function(x) {
    return( abs( x[length(x)] - mean(x) ) )
}

for(col.name in names(train)) {
    if( !(col.name %in% c("P8","V7","V9")) ) {
        print(col.name)
        sum.all.lag.func.values <- 0
        trial.counter<-0
        for(train.trial in split(train,train$TrialID)) {
            print(trial.counter)
            trial.counter <- trial.counter + 1 

            all.lag.periods <- c()
            all.lag.func.values <- c()
            c.tmp <- train.trial[[col.name]] 
            # data to use is defined in function below for c
            # c  <- as.zoo(  c.tmp - lagcol(c.tmp,100) )
            c  <- as.zoo(  c.tmp  ) 
            for(lag.periods in LAGS) {  
                # function in rollapply below is StdDev (sd), or meanfreq 
                ff <- as.vector( rollapply(c, lag.periods, xminusmean, align="right", na.pad=TRUE ))
                ff[ !is.finite(ff) ] <- 0 # median(ff, na.rm=TRUE)

                lagged.func.value <- cor( train.trial$IsAlert,  ff )
                lagged.func.value[!is.finite(lagged.func.value)] <- 0 
                all.lag.periods <- c(all.lag.periods, lag.periods)
                all.lag.func.values <- c(all.lag.func.values, lagged.func.value)
            }
            sum.all.lag.func.values <- sum.all.lag.func.values + all.lag.func.values
        }
        plot(log10(all.lag.periods), sum.all.lag.func.values, main=col.name, type="l")      
    }
}






