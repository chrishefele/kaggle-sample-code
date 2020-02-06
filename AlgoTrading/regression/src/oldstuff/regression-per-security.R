# Basic regression on source data (& perhaps other features)

library(glmnet)

#st<-system.time( load(file="/home/chefele/AlgoTrading/data/probe.Rsave") )
#print(st)
st<-system.time( load(file="/home/chefele/AlgoTrading/data/training.Rsave") )
print(st)

#source("/home/chefele/AlgoTrading/features/src/makeFeatures.R")
#st<- system.time(features <- makeFeatures(training))
#print(st)
load("/home/chefele/AlgoTrading/features/training.features.Rsave")

# --- internal constants

pre.tperiods  <- 1:50
post.tperiods <- 51:100
event.tperiod <- 50

mkNames   <- function(ask.or.bid, periods) { paste(ask.or.bid, as.character(periods),sep="") }
pre.bids  <- mkNames("bid", pre.tperiods)
pre.asks  <- mkNames("ask", pre.tperiods)
post.bids <- mkNames("bid", post.tperiods)
post.asks <- mkNames("ask", post.tperiods)
event.ask <- mkNames("ask", event.tperiod)
event.bid <- mkNames("bid", event.tperiod)

INIT_BUY  <- "B"
INIT_SELL <- "S"

security_ids <- sort(unique(training$security_id))
initiators   <- sort(unique(training$initiator))

#security_ids <- c(2)     # FOR TESTING ONLY 
#initiators   <- c("B")   # FOR TESTING ONLY 

# --- main

pdf(file="regression-per-security.pdf")  # FOR TESTING
par(mfrow=c(2,2))

fitModel <- function(X,Y,tag) {
    print(paste("Fitting model for:",tag))
    st<-system.time( fit<-cv.glmnet(X, Y, family="gaussian") )
    plot(fit, main=tag)
    print(coef(fit))
    print(fit)
    print(st)
    return(fit)
}

selectMask <- function(df, sid, initr) { df$security_id==sid & df$initiator==initr  } 


for(security_id in security_ids) {
    for(initiator in initiators) {

        dat  <- training[          selectMask(training, security_id, initiator), ]  
        fdat <- training.features[ selectMask(training, security_id, initiator), ]  
        tag <- paste(   "sec_id:",as.character(security_id), "init:", initiator, 
                        "nrows:", as.character(nrow(dat))   )
        print(tag)

        # set the reference/centering levels for buys & sells & bids & asks (possibly) seperately 
        if(initiator == INIT_BUY) {   
            ask.ref <- dat[,event.ask]  
            bid.ref <- ask.ref
            #bid.ref <- dat[,event.bid]   # default
        } else {
            bid.ref <- dat[,event.bid]
            ask.ref <- bid.ref 
            # ask.ref <- dat[,event.ask]  # default
        }

        X.bidasks <- as.matrix(cbind(    dat[,pre.asks]    - ask.ref,       
                                         dat[,pre.bids]    - bid.ref ))   # center on event bid/ask
        X.features<- as.matrix(cbind(fdat))

        Y.asks    <- as.matrix(rowMeans( dat[,post.asks] ) - ask.ref)     # center on event bid/ask
        Y.bids    <- as.matrix(rowMeans( dat[,post.bids] ) - bid.ref)

        #fit.asks <- fitModel(X.bidasks, Y.asks, paste("asks",tag))
        #fit.bids <- fitModel(X.bidasks, Y.bids, paste("bids",tag))
        fit.asks <- fitModel(X.features, Y.asks, paste("asks",tag))
        fit.bids <- fitModel(X.features, Y.bids, paste("bids",tag))
    }
}

stop()

# Write test set probability predictions to a file

Prediction <- predict( fit.train, newx=X.test, s=LAMBDA, type="response")
TrialID <- test$TrialID
ObsNum <- test$ObsNum
submission.data <- data.frame(TrialID, ObsNum, Prediction )
write.csv(submission.data, file=SUBMISSION_FILE, row.names=FALSE,col.names=TRUE)

