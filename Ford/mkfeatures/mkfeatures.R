# R program for "Stay Alert! The Ford Challenge" on Kaggle.com
# Program reads original data, creates & writes features files for fitting by another program
# 2/15/2011 by Chris Hefele
#

library(zoo)

TRAINING_FILE       <- "/home/chefele/Ford/download/fordTrain.csv"
TEST_FILE           <- "/home/chefele/Ford/download/fordTest.csv"

TRAIN_FEATURES_FILE <- "fordTrain.features.csv"
TEST_FEATURES_FILE  <- "fordTest.features.csv" 


object.sizes <- function() {  # utility function used to monitor memory consumption 
    return(rev(sort(sapply(ls(envir=.GlobalEnv), function (object.name)
    object.size(get(object.name))))))
}

# Define functions to select/transform the raw input data 

logmin <- function(x) { log(x-min(x)+1.0) } # makes lognormal hists more normal

flip.below.median <- function(x) {   # inverts order of all values below median
    mask <- (x < median(x))          # used to improve E10 only 
    xout <- x
    xout[mask] <- -xout[mask] + median(x) 
    return( xout ) 
}

make.X.dataframe <- function(x) {       
    Xout <- data.frame( 
        logmin(x$P1),
        logmin(x$P2), #looks like high-freq noise (4 sample cycle); EEG? ZCR? LPFilter?
        logmin(x$P3),
        logmin(x$P4),
        logmin(x$P5),
        logmin(x$P6),
        x$P7,
        # x$P8, # ignore; all const 
        logmin(x$E1),
        x$E2,            # range 0-360, so something circular? steering wheel? 
        abs(x$E2-180.0), # lowers value if rotate in either direction
        x$E3,
        x$E4,
        x$E5,
        x$E6,
        logmin(x$E7),
        logmin(x$E8),
        x$E9,
        x$E10, # looks like speed! 25-80, lots at 70 exactly
        flip.below.median(x$E10),  # ROC shows antipredictive below median, so fix this
        x$E11, 
        x$V1,
        x$V2,
        x$V3,
        logmin(x$V4),
        x$V5,
        x$V6,
        # x$V7, # ignore; all const
        x$V8,
        # x$V9, # ignore; all const
        x$V10,
        logmin(x$V11) # low correlation, but highest AUC alone 
    )
    return(Xout) 
}

# Define functions for creating new features 

apply.func <- function(x,func,t.window) {  # apply func (from below) using sliding window
    xzoo <- as.zoo(x)
    retval <- as.vector( rollapply(xzoo, t.window, func, align="right", na.pad=TRUE ))
    retval[ !is.finite(retval) ] <- median(retval, na.rm=TRUE)
    return( retval ) 
}

diff.vs.mean            <- function(x)      { x[length(x)] - mean(x) } 
diff.func               <- function(x)      { x[length(x)] - x[1] } 
lag.func                <- function(x)      { x[1] } 
rolling.diff            <- function(x,tlag) { apply.func(x,diff.func,tlag) }
rolling.lag             <- function(x,tlag) { apply.func(x,lag.func,tlag)  } 
rolling.lag.10          <- function(x)      { rolling.lag(x,10)  } 
rolling.lag.100         <- function(x)      { rolling.lag(x,100) }
abs.rolling.diff        <- function(x)      { abs(rolling.diff(x,30)) } 
rolling.diff.vs.mean    <- function(x)      { apply.func(x,diff.vs.mean, 100) } 
abs.rolling.diff.vs.mean<- function(x)      { abs(rolling.diff.vs.mean(x)) } 
rolling.sd              <- function(x)      { apply.func(x,sd,10) } 
rolling.diff.vs.mean    <- function(x)      { apply.func(x, diff.vs.mean, 100) }
meanfreq                <- function(x)      {
    full.pwr.spectrum <- Mod( fft(x) )^2
    first.half.freqs <- 1:(length(full.pwr.spectrum)/2)
    pwr.spectrum <- full.pwr.spectrum[ first.half.freqs ]  
    mean.freq <- sum( pwr.spectrum*(first.half.freqs-1) ) / sum( pwr.spectrum ) 
    return( mean.freq ) 
}
rolling.meanfreq        <- function(x)      { apply.func(x, meanfreq, 16) } 

FUNCTION.NAMES <- c(        # list of functions used to create new features          
    "rolling.lag.10",          
    "rolling.lag.100",   
    "abs.rolling.diff",     
    "rolling.diff.vs.mean",         
    "abs.rolling.diff.vs.mean", 
    "rolling.sd",               
    "rolling.meanfreq" 
)      


make.FX.dataframe <- function(df.in) {   # create new dataframe as functions of another
    df.out <- data.frame( dummy=1:nrow(df.in) ) #sets right dataframe size 
    for(col.name in names(df.in)) { 
        for(func.name in FUNCTION.NAMES) {
            func.to.apply <- get(func.name) 
            new.col.name <- paste( col.name, "__",func.name, sep="" )
            print(new.col.name)
            df.out[[new.col.name]] <- func.to.apply( df.in[[col.name]]  )
        }
        print( object.size(df.out) ) 
    }
    df.out$dummy <- NULL 
    return( df.out ) 
}


# OK, let's go. Get & transform the data, then write the feature files

test  <- read.csv(TEST_FILE)
train <- read.csv(TRAINING_FILE)

X0.test   <- make.X.dataframe(test)
X.test    <- scale( cbind( as.matrix(X0.test),  as.matrix(make.FX.dataframe(X0.test)) ))
write.csv(X.test, file=TEST_FEATURES_FILE, row.names=FALSE,col.names=TRUE)

X0.train  <- make.X.dataframe(train)
X.train   <- scale( cbind( as.matrix(X0.train), as.matrix(make.FX.dataframe(X0.train)) ))
write.csv(X.train, file=TRAIN_FEATURES_FILE, row.names=FALSE,col.names=TRUE)

print("Done")

