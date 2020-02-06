LAGS <- as.integer( (1.07)^c(1:136) )

train <- read.csv("/home/chefele/Ford/download/fordTrain.csv")
pdf(file="vary.lag.plots.pdf")

lagcol <- function(the.col, the.lag) {     # timelag a vector of data
    end.index <- length(the.col) - the.lag
    padding <- rep( the.col[1], the.lag ) 
    return(  c( padding, the.col[1:end.index] ) )
}


for(col.name in names(train)) {
    if( !(col.name %in% c("P8","V7","V9")) ) {
        print(col.name)
        all.lag.periods <- c()
        all.lag.func.values <- c()
        for(lag.periods in LAGS) {
            # print(lag.periods)
            c <- train[[col.name]]
            lagged.func.value <- cor( train$IsAlert, (c-lagcol(c,lag.periods)) )
            all.lag.periods <- c(all.lag.periods, lag.periods)
            all.lag.func.values <- c(all.lag.func.values, lagged.func.value)
        }
        plot(log10(all.lag.periods), all.lag.func.values, main=col.name, type="l")      
    }
}

