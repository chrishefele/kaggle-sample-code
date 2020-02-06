

train <- read.csv("/home/chefele/Ford/download/fordTrain.csv")
pdf(file="vary.lag.plots.nooverlap.pdf")

lagcol <- function(the.col, the.lag) {     # timelag a vector of data
    end.index <- length(the.col) - the.lag
    padding <- rep( the.col[1], the.lag ) 
    return(  c( padding, the.col[1:end.index] ) )
}

myCCF  <- function(dfin) {  
            the.ccf <- ccf( dfin$X, dfin$Y, lag.max=300, plot=FALSE ) 
            return( the.ccf[[1]] ) 
        }

for(col.name in names(train)) {
    if( !(col.name %in% c("TrialID", "P8","V7","V9")) ) {
        print(col.name)

        c <- train[[col.name]]
        target <- train$IsAlert
        df <- data.frame(X=train[[col.name]], Y=train$IsAlert, TID=train$TrialID )

        rslts <- by( df, df$TID, myCCF )  
        sum.rslts <- 0 
        for(rslt in rslts) {
            sum.rslts <- sum.rslts + rslt
        }

        plot(sum.rslts, main=col.name, type="l")      
    }
}

