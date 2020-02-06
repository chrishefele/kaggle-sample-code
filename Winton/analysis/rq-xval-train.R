
library("rqPen")

RETURNS.FILE  <- "../data/train.RData"
PLOT.FILE     <-"rq-xval-train.pdf"
NFOLDS        <- 5 # for cv.rq.pen nfold xval model 

t.pred.start  <- 121
#t.pred.end    <- 180
t.pred.end    <- 121
t.train.width <- 120 - 2 + 1 

pdf(file=PLOT.FILE)

train <- readRDS(RETURNS.FILE)
train[is.na(train)] <- 0
rownames(train) <- train$Id
train <- train[order(train$Feature_7, train$Id),]
f7s <- sort(unique(train$Feature_7))

errs.zero <- 0
errs.rq   <- 0
errs.cvrq <- 0
n.preds   <- 0 

for(t.pred in t.pred.start:t.pred.end) {
    for(f7 in f7s) {

        row.select <- train$Feature_7 == f7 
        t.train.end   <- t.pred - 1 
        t.train.start <- t.train.end - t.train.width + 1 
        x.col.select <- paste("Ret",  t.train.start   : t.train.end,    sep="_")
        y.col.select <- paste("Ret", (t.train.start+1):(t.train.end+1), sep="_")
        x.returns <- t(train[row.select, x.col.select]) # so row=time, col=stock.id
        y.returns <- t(train[row.select, y.col.select]) # so row=time, col=stock.id

        # train then predict each stock in the f7 group 
        for(stock.id in colnames(x.returns)) { 

            n.preds <- n.preds + 1

            #x <- x.returns            # use all stocks in f7 group
            x <- x.returns[,stock.id, drop=FALSE] # use only same stock 
            #
            noise <- rnorm(nrow(x)) * sd(x)
            x <- cbind(x, noise)
            x <- jitter(x, factor=0.1)

            y <- y.returns[,stock.id]
            y <- jitter(y, factor=0.1)

            x.train <- x[1:(nrow(x)-1), ,drop=FALSE]
            x.test  <- x[   nrow(x)   , ,drop=FALSE]
            y.train <- y[1:(nrow(x)-1) ]
            y.test  <- y[   nrow(x)    ]

            cat("\n----------------------------------------------\n")
            cat("modeling ", "t.pred:", t.pred, "f7:", f7, 
                             "-> stock.id:", stock.id, "\n")

            cat("\nrq.model\n")
            rq.model   <- rq(y.train ~ 0 + x.train) # or just x.train 
            #rq.model  <- rq(y.train ~     x.train) # or just x.train 
            print(coef(rq.model))

            cat("\ncv.rq.model\n")
            cv.rq.model <- cv.rq.pen(x.train, y.train, 
                                    intercept=FALSE, nfolds=NFOLDS)  #intercept FALSE?

            coefs <- coef(cv.rq.model)
            print(coefs[coefs!=0])
            cat("\n")

            # section to compare to TRAINING data
            #preds.zero  <- 0
            #preds.rq    <- predict(rq.model,    newdata=as.data.frame(x.train))
            #preds.cvrq  <- predict(cv.rq.model, newx=x.train)[,1]
            #errs.zero <- errs.zero + sum(abs(y.train - preds.zero))
            #errs.rq   <- errs.rq   + sum(abs(y.train - preds.rq  ))
            #errs.cvrq <- errs.cvrq + sum(abs(y.train - preds.cvrq))

            # section to compare to TEST data (e.g. Ret_121)
            preds.zero  <- 0
            preds.rq    <- predict(rq.model,    newdata=as.data.frame(x.test))
            preds.cvrq  <- predict(cv.rq.model, newx=x.test)[,1]
            errs.zero <- errs.zero + sum(abs(y.test - preds.zero))
            errs.rq   <- errs.rq   + sum(abs(y.test - preds.rq  ))
            errs.cvrq <- errs.cvrq + sum(abs(y.test - preds.cvrq))

            cvrq.gain <- round(100 * (errs.zero - errs.cvrq)/errs.zero, digits=4)
            cat("TOTERROR:", 
                " n.preds: ",   n.preds, 
                " errs.zero: ", errs.zero, 
                " errs.rq: ",   errs.rq, 
                " errs.cvrq: ", errs.cvrq, 
                " cvrq.gain: ", cvrq.gain, " %", "\n")

        }
    }
}


