LAGS <- as.integer( (1.07)^c(1:90) )

train <- read.csv("/home/chefele/Ford/download/fordTrain.csv")
pdf(file="lagplot.origvars.pdf")

lagcol <- function(the.col, the.lag) {     # timelag a vector of data
    end.index <- length(the.col) - the.lag
    padding <- rep( the.col[1], the.lag ) 
    return(  c( padding, the.col[1:end.index] ) )
}


for(col.name in names(train)) {
    if( !(col.name %in% c("P8","V7","V9")) ) {
        print(col.name)
        sum.all.lag.func.values <- 0
        for(train.trial in split(train,train$TrialID)) {
            all.lag.periods <- c()
            all.lag.func.values <- c()
            c <- train.trial[[col.name]]
            for(lag.periods in LAGS) {
                lagged.func.value <- cor( train.trial$IsAlert, lagcol(c,lag.periods)  )
                lagged.func.value[!is.finite(lagged.func.value)] <- 0 
                all.lag.periods <- c(all.lag.periods, lag.periods)
                all.lag.func.values <- c(all.lag.func.values, lagged.func.value)
            }
            sum.all.lag.func.values <- sum.all.lag.func.values + all.lag.func.values
        }
        plot(log10(all.lag.periods), sum.all.lag.func.values, main=col.name, type="l")      
    }
}

