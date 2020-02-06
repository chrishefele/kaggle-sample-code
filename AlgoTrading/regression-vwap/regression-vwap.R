# regression-vwap.R  
# by Chris Hefele December, 2011
# Basic regression on source data (& perhaps other features)
# for the Algorithmic Trading Challenge on Kaggle.com 
#
# DIFFERS from regression.R since it divides all prices by VWAP
# so it might be more scale invariant; perhaps good for blending?

# --- command line arg processing 

# optionally invoke script with a specific timeslot to predict (51...100):
#    cat regression.R | R --vanilla --args <t.prediction> | tee regression.log

t.prediction <- as.integer(commandArgs(trailingOnly=TRUE)[1])
if(is.na(t.prediction)) {  # no or improper arg specified ; must be 51...100
    DYNAMIC_PREDICTIONS <- FALSE # predict const bid or ask for all timeslots
} else {
    DYNAMIC_PREDICTIONS <- TRUE  # predict one specific timeslot
}
print(DYNAMIC_PREDICTIONS)
print(t.prediction)

# --- configurable constants

library(glmnet)

DATA_DIR        <- "/home/chefele/AlgoTrading/data/"
FEATURE_DIR     <- "/home/chefele/AlgoTrading/features/"
DYNAMIC_DIR     <- "dynamics.cache/"  # temporary output directory for dynamic predictions

PLOT_FILE       <- "regression-vwap.plots.pdf"
SUBMISSION_FILE <- "regression-vwap.testing.csv"
PROBE_FILE      <- "regression-vwap.probe.csv"

load(paste(DATA_DIR,    "probe.Rsave",    sep="")) 
load(paste(DATA_DIR,    "testing.Rsave",  sep="")) 
load(paste(DATA_DIR,    "training.Rsave", sep="")) 

load(paste(FEATURE_DIR, "probe.features.Rsave",    sep="")) 
load(paste(FEATURE_DIR, "testing.features.Rsave",  sep="")) 
load(paste(FEATURE_DIR, "training.features.Rsave", sep="")) 

# --- internal constants

t.event <- 50
t.pre   <- 1:50  
t.post  <- 51:100
t.post51<- 52:100
t.51    <- 51
t.50    <- 50

mkNames   <- function(ask.or.bid, periods) { paste(ask.or.bid, as.character(periods),sep="") }
bid.names.pre   <- mkNames("bid", t.pre  )
ask.names.pre   <- mkNames("ask", t.pre  )
bid.names.post  <- mkNames("bid", t.post )
ask.names.post  <- mkNames("ask", t.post )

bid.names.post51<- mkNames("bid", t.post51 )
ask.names.post51<- mkNames("ask", t.post51 )
bid.names.51    <- mkNames("bid", t.51 )
ask.names.51    <- mkNames("ask", t.51 )
bid.names.50    <- mkNames("bid", t.50 )
ask.names.50    <- mkNames("ask", t.50 )

bid.names.prediction    <- mkNames("bid", t.prediction)
ask.names.prediction    <- mkNames("ask", t.prediction)
bidask.names.prediction <- as.vector(rbind(bid.names.prediction,ask.names.prediction))

bid.names.event <- mkNames("bid", t.event)
ask.names.event <- mkNames("ask", t.event)
bidask.names.post <- as.vector(rbind(bid.names.post,ask.names.post))

if(DYNAMIC_PREDICTIONS) {
    #target.ask.names.post <- as.list(ask.names.post51) # predict T52..T100 individually
    #target.bid.names.post <- as.list(bid.names.post51) # thus time-varying predictions
    if(t.prediction==51) { # skip calculating the prediction which I prepopulate anyway
        target.ask.names.post <- list()
        target.bid.names.post <- list()
    } else {
        target.ask.names.post <- as.list(ask.names.prediction) # predict one timeslot individually
        target.bid.names.post <- as.list(bid.names.prediction) # to assmble time-varying predictions later
    }
} else { 
    target.ask.names.post <- list(ask.names.post51)    # predict avg of T52..T100 together
    target.bid.names.post <- list(bid.names.post51)    # thus time-constant prediction
    #target.ask.names.post <- list(ask.names.post)    # predict avg of T51..T100 together
    #target.bid.names.post <- list(bid.names.post)    # thus time-constant prediction
}

INIT_BUY  <- "B"
INIT_SELL <- "S"
INITIATORS <- c(INIT_BUY, INIT_SELL)


# --- utility functions

fitModel <- function(X,X.wts, Y,tag) {
    print(paste("Fitting model for:",tag))
    st<-system.time( fit<-cv.glmnet(X, Y, weights=X.wts, family="gaussian") ) 
    plot(fit, main=tag)
    print(coef(fit))
    print(fit)
    print(st)
    return(fit)
}

# reference level functions used to 'center' the data differently for buys vs sells
#initRef <- function(i,d) { if(i==INIT_BUY) d[d$initiator==i,ask.names.event] 
#                           else            d[d$initiator==i,bid.names.event] }
#askRef  <- function(i,d) { initRef(i,d) }  # or...d[ask.names.event]
#bidRef  <- function(i,d) { initRef(i,d) }  # or...d[bid.names.event]

# make X matrix for regression by compiling bid/ask (centered) prices & feature data
makeX   <- function(init, prices, features) {   
        print("Making X")
        init.mask <- prices$initiator == init
        as.matrix(cbind(  prices[init.mask,ask.names.pre] / prices[init.mask,"trade_vwap"],       
                          prices[init.mask,bid.names.pre] / prices[init.mask,"trade_vwap"], 
                          features[init.mask,]  
        ))   
}

price.sd <- function(df, names.pre) {
        sid <- df$security_id
        prices.pre  <- as.matrix(cbind( df[,names.pre] / df$trade_vwap )) 
        prices.sd   <- tapply( apply(prices.pre,1,sd), sid, mean)
        return(prices.sd)
}

makeXwts <- function(init, training.data, target.data, features) {  # makes per-security row weights for training 
        print("Making X weights")

        # Weight each security by the ratio that security's row-counts in probe/testing vs in training. 
        ratio.counts <- table(target.data$security_id) / table(training.data$security_id) 
        
        # Weight each security by the ratio of their avg standard deviations of bids & asks
        if(FALSE) { # switchable, since this segment is a bit slow ~10 minutes
            print("  X-weights: sd")
            training.asks.sd <- price.sd(training.data, ask.names.pre) # per-security sd(asks)
            training.bids.sd <- price.sd(training.data, bid.names.pre)
            target.asks.sd   <- price.sd(target.data,   ask.names.pre)
            target.bids.sd   <- price.sd(target.data,   bid.names.pre)
            ratio.sds        <- (target.asks.sd + target.bids.sd) / (training.asks.sd + training.bids.sd)
        }
        
        # Weight each security by the ratio of their average vwaps
        print("  X-weights: vwaps")
        ratio.vwaps      <- tapply( target.data$trade_vwap,   target.data$security_id,   mean) /
                            tapply( training.data$trade_vwap, training.data$security_id, mean) 

        # Weight each security by the ratio of their average spreads at T50
        print("  X-weights: spread50s")
        ratio.spread50s  <- tapply( (target.data$ask50  -target.data$bid50  )/target.data$trade_vwap, 
                                                                              target.data$security_id,   mean) /
                            tapply( (training.data$ask50-training.data$bid50)/training.data$trade_vwap, 
                                                                               training.data$security_id, mean)

        # **** PICK ONLY ONE OF THE METHODS BELOW
        #security.weights <- 0*ratio.counts+1 # rmse 1.23199191853512  even weights
        security.weights <- ratio.counts     # rmse 1.2285516836339
        #security.weights <- ratio.sds        # rmse 1.22557444672192
        #security.weights <- ratio.vwaps      # rmse 1.22664314240695
        #security.weights <- ratio.spread50s  # rmse 1.23123362893101
        #security.weights <- ratio.counts *  ratio.sds       # rmse 1.22808726067375
        #security.weights <- ratio.counts *  ratio.vwaps     # rmse  1.22963488781138
        #security.weights <- ratio.counts *  ratio.spread50s # rmse 1.22925455751895
        #security.weights <- ratio.vwaps^2    # rmse 1.2275440891953"
        #security.weights <- sqrt(ratio.vwaps) # rmse 1.22722638641115"

        row.weights <- security.weights[ as.character(training.data$security_id) ] 
        init.mask <- training.data$initiator == init
        print("Done making X weights")
        return(row.weights[init.mask])
}

# Y to predict is just the mean of one or many bids/asks 
makeY <- function(init, prices, price.names) {  # NOTE: price.offset removed in this version
        print("Making Y for:")
        print(price.names)
        #as.matrix( rowMeans(prices[prices$initiator==init,  price.names] ) - price.offset ) 
        mask <- prices$initiator==init 
        as.matrix( rowMeans(prices[mask,][price.names]) / prices[mask,"trade_vwap"] ) 
}

myPredict  <- function(fit.model, new.X, vwaps) {  # NOTE: price offset unused in this version
        print("Making predictions")
        #predict(fit.model,newx=new.X) + price.offset  
        predict(fit.model,newx=new.X) * vwaps
}

# --- main

pdf(file=PLOT_FILE)  

# create output dataframes, which will be overwritten with predictions
# also include the 'free' prediction (it's known that t51 bid/ask == t50 bid/ask)
preds.probe   <- data.frame(row_id=probe$row_id)
preds.probe[  ,bidask.names.post] <- -1
preds.probe[  ,bid.names.51] <- probe[ ,bid.names.50]     # Known that t50==t51
preds.probe[  ,ask.names.51] <- probe[ ,ask.names.50]

preds.testing <- data.frame(row_id=testing$row_id)
preds.testing[,bidask.names.post] <- -1
preds.testing[  ,bid.names.51] <- testing[ ,bid.names.50] # Known that t50==t51
preds.testing[  ,ask.names.51] <- testing[ ,ask.names.50]


nitems <- length(target.ask.names.post)
for(i in 1:nitems ) {
    if(nitems==0) { next }  # skips 1:0 case where number nothing to compute, i.e. T51
    target.ask.name.post <- target.ask.names.post[[i]]
    target.bid.name.post <- target.bid.names.post[[i]]
    print(" ")
    print("Switching to OUTPUT_VARIABLES:")
    print(target.ask.name.post)
    print(target.bid.name.post)

    for(initiator in INITIATORS) {
        tag <- paste("init:", initiator)
        print(tag)
            
        # create training data to train 2 regressions (1 for bid, 1 for ask) 
        X         <- makeX(   initiator, training, training.features)
        Xwts      <- makeXwts(initiator, training, probe, training.features)   # *** TUNABLE!!! probe or training
        #Y.asks    <- makeY(initiator, training, ask.names.post, askRef(initiator,training) ) 
        #Y.bids    <- makeY(initiator, training, bid.names.post, bidRef(initiator,training) ) 
        Y.asks    <- makeY(initiator, training, target.ask.name.post) 
        Y.bids    <- makeY(initiator, training, target.bid.name.post)
        fit.asks <- fitModel(X, Xwts, Y.asks, paste("asks",tag))
        fit.bids <- fitModel(X, Xwts, Y.bids, paste("bids",tag))
          
        # make probe predictions
        X <- makeX(initiator, probe, probe.features)
        imask <- probe$initiator == initiator
        vwaps.probe <- probe[imask,"trade_vwap"] 
        #preds.probe[imask, ask.names.post] <- myPredict(fit.asks, X, askRef(initiator,probe))
        #preds.probe[imask, bid.names.post] <- myPredict(fit.bids, X, bidRef(initiator,probe))
        preds.probe[imask, target.ask.name.post] <- myPredict(fit.asks, X, vwaps.probe)
        preds.probe[imask, target.bid.name.post] <- myPredict(fit.bids, X, vwaps.probe)

        # make testing predictions
        X <- makeX(initiator, testing, testing.features)
        imask <- testing$initiator == initiator
        vwaps.testing <- testing[imask,"trade_vwap"] 
        #preds.testing[imask, ask.names.post] <- myPredict(fit.asks, X, askRef(initiator,testing))
        #preds.testing[imask, bid.names.post] <- myPredict(fit.bids, X, bidRef(initiator,testing))
        preds.testing[imask, target.ask.name.post] <- myPredict(fit.asks, X, vwaps.testing)
        preds.testing[imask, target.bid.name.post] <- myPredict(fit.bids, X, vwaps.testing)

        print("Starting garbage collection")
        print(gc())
    }

    print("Starting garbage collection")
    print(gc())
} 


if(DYNAMIC_PREDICTIONS) {
    errs <- as.matrix(preds.probe[,bidask.names.prediction] - probe[,bidask.names.prediction])
} else {
    errs <- as.matrix(preds.probe[,bidask.names.post]       - probe[,bidask.names.post])
}
rmse <- sqrt(mean(errs*errs))
print(paste("RMSE of probe predictions:", as.character(rmse)))


writeFile <- function(df, tag1, tag2) { 
    fname <- paste(DYNAMIC_DIR, tag1, tag2, ".csv", sep="")  
    print(paste("Writing:",fname))
    write.csv(df, file=fname, quote=FALSE, row.names=FALSE, col.names=TRUE )
}

if(DYNAMIC_PREDICTIONS) {
    writeFile( preds.probe[  "row_id"],                  "probe.",   "row_id" )
    writeFile( preds.testing["row_id"],                  "testing.", "row_id" )
    writeFile( preds.probe[  , bidask.names.prediction], "probe.t",   as.character(t.prediction) )
    writeFile( preds.testing[, bidask.names.prediction], "testing.t", as.character(t.prediction) )
} else {
    print(paste("Writing submission file to:", SUBMISSION_FILE))
    write.csv(preds.testing, file=SUBMISSION_FILE, quote=FALSE, row.names=FALSE, col.names=TRUE)
    print(paste("Writing probe file to:", PROBE_FILE))
    write.csv(preds.probe,   file=PROBE_FILE,      quote=FALSE, row.names=FALSE, col.names=TRUE)
}

print("Done.")


