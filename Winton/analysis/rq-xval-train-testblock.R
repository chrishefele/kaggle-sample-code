
library("rqPen")

NFOLDS        <- 5 # for cv.rq.pen nfold xval model 
RETURNS.FILE  <- "../data/train.RData"
PLOT.FILE     <-"rq-xval-train-testblock.pdf"

t.train.start <- 2
t.train.end   <- 120 
t.test.start  <- 121
t.test.end    <- 180 - 1 # -1 due to y lag 

pdf(file=PLOT.FILE)

train <- readRDS(RETURNS.FILE)
train[is.na(train)] <- 0
rownames(train) <- train$Id
train <- train[order(train$Feature_7, train$Id),]
f7s <- sort(unique(train$Feature_7))

errs.zero <- 0
errs.cvrq <- 0
n.preds   <- 0 

for(f7 in f7s) {

    row.select <- train$Feature_7 == f7 

    x.train.select <- paste("Ret",  t.train.start   : t.train.end,    sep="_")
    y.train.select <- paste("Ret", (t.train.start+1):(t.train.end+1), sep="_")
    x.train <- t(train[row.select, x.train.select]) # so row=time, col=stock.id
    y.train <- t(train[row.select, y.train.select]) # so row=time, col=stock.id

    x.test.select <- paste("Ret",  t.test.start   : t.test.end,    sep="_")
    y.test.select <- paste("Ret", (t.test.start+1):(t.test.end+1), sep="_")
    x.test <- t(train[row.select, x.test.select]) # so row=time, col=stock.id
    y.test <- t(train[row.select, y.test.select]) # so row=time, col=stock.id

    # train then predict each stock in the f7 group 
    for(stock.id in colnames(x.train)) { 

        n.preds <- n.preds + 1

        # train the models on the returns in the training columns

        cat("\n----------------------------------------------\n")
        cat("cv.rq modeling ", "f7:", f7, "-> stock.id:", stock.id, "\n")
        x <- jitter(x.train, factor=0.1)
        y <- jitter(y.train[,stock.id], factor=0.1)

        cv.rq.model <- cv.rq.pen(x, y, 
                                intercept=TRUE, nfolds=NFOLDS)  #intercept FALSE?
        coefs <- coef(cv.rq.model)
        print(coefs[coefs!=0])
        cat("\n")

        # evaluate the model predictions using returns in the test columns 
        preds.zero  <- 0
        preds.cvrq  <- predict(cv.rq.model, newx=x.test)[,1]
        y.actual    <- y.test[,stock.id]
        errs.zero   <- errs.zero + sum(abs(y.actual - preds.zero))
        errs.cvrq   <- errs.cvrq + sum(abs(y.actual - preds.cvrq))

        cvrq.gain <- round(100 * (errs.zero - errs.cvrq)/errs.zero, digits=4)
        cat("ERRORS", 
            " n: ",         n.preds, 
            " id: ",        stock.id, 
            " f7: ",        f7,  
            " errs.zero: ", round(errs.zero, digits=4), 
            " errs.cvrq: ", round(errs.cvrq, digits=4),
            " cvrq.gain: ", cvrq.gain, " %", "\n")

    }
}


