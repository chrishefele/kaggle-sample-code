
library("quantreg")
library("rqPen")
library("glmnet")
library("randomForest")

# -------------------- Constants / parameters

FEATURES_X_FILE  <- "../../data/train.RData"
PLOT_FILE        <- "pred-abs-rp2-perstock.pdf"
pdf(file=PLOT_FILE)
NFOLDS           <- 10

# -------------------- Create X & Y variables for modeling

cat("Reading X features from: ", FEATURES_X_FILE,"\n")
x.raw <- readRDS(file=FEATURES_X_FILE)
x.raw[is.na(x.raw)] <- 0
cat("X features have the following dimensions: ", dim(x.raw),"\n")

target.col <- "Ret_PlusTwo"
cat("target column: ", target.col, "\n")
stopifnot(target.col %in% c("Ret_PlusOne","Ret_PlusTwo"))

y  <- abs(x.raw[,target.col])  # NOTE: *** absolute value of return, NOT return

feature.cols  <- paste("Feature", c(1:6, 8:25), sep="_")
intraday.cols <- paste("Ret", 2:120, sep="_")
x <- x.raw[,feature.cols]
x[,"sumAbsIntraday"]   <- rowSums(abs(x.raw[,intraday.cols]))
x[,"meanAbsRetMinus12"] <- (abs(x.raw[,"Ret_MinusOne"]) + abs(x.raw[,"Ret_MinusTwo"]) ) / 2.
x[,"absMeanRetMinus12"] <- abs(x.raw[,"Ret_MinusOne"] + x.raw[,"Ret_MinusTwo"]) / 2.
x[,"absSumIntraday"]    <- abs(rowSums(x.raw[,intraday.cols]))
x <- cbind(x, data.frame(rnd1=rnorm(length(y)), rnd2=rnorm(length(y))))

# add random variables
#for(rand.col in paste("Rand", c(1:20), sep="_")) {
#    x[,rand.col] <- rnorm(nrow(x))
#}

cat("Head of X\n")
print(head(x))

# -------------------- Simple correlations

cat("Simple rank correlations with Y\n")
y.df <- data.frame(y)
cors <- cor(x, y.df, method="spearman")
print(round( cors, digits=3))

# -------------------- GLMNET regularized linear regression model 

if(TRUE) {

    cat("\n\nTraining GLMNET model\n")
    X.train <- as.matrix(x)
    Y.train <- y

    st <- system.time( 
        fit.train <- cv.glmnet(X.train, Y.train, type.measure="mse", family="gaussian") 
    )

    # Output various stats & plots for analysis later...
    cat("Finished training in : ", st, "\n")
    cat("\n\nGLMNET results:\n")
    print(coef(fit.train))
    print(fit.train)

    min.mse      <- min(fit.train$cvm)
    pseudo.rsq   <- 1. - min.mse / var(y)
    cat("RESULT glmnet minMSE: ", min.mse, " pseudoRSq: ", pseudo.rsq, "\n")

    plot(fit.train)

}

# -------------------- RandomForest model

if(TRUE) {
    NTREE <- 250
    TREE_NODE_SIZE <- 20

    cat("\n\nTraining RANDOMFOREST model\n")
    rf <- randomForest(x, y, 
                       ntree=NTREE, 
                       nodesize=TREE_NODE_SIZE, 
                       importance=TRUE, 
                       do.trace=TRUE ) 

    print("ERRORS")
    print(rf$mse)
    min.mse <- min(rf$mse)
    cat("RESULT randomForest minMSE:", min.mse, " pseudoRSq ", max(rf$rsq), "\n")

    cat("VARIABLE IMPORTANCE\n")
    rf.imp <- as.data.frame(importance(rf))
    print(rf.imp)

    cat("SORTED VARIABLE IMPORTANCE\n")
    sort.field <- "%IncMSE"   # other option is: "IncNodePurity"
    rf.imp.sort <- rf.imp[ order(rf.imp[[sort.field]], decreasing=TRUE) , ]
    print(rf.imp.sort)

}


# -------------------- quantile regression 
if(FALSE) {

    errs <- c(0,0,0)
    groups <- sort(unique(x.raw[,"Feature_7"]))
    for(group in groups) {
        mask <- group == x.raw[,"Feature_7"]
        y.group <- y[mask ]
        x.group <- x[mask,]

        cat("Training cv.rq model for group: ", group, "\n") 
        x.group <- jitter(x.group, factor=0.1)
        y.group <- jitter(y.group, factor=0.1)

        cv.rq.model  <- cv.rq.pen(x.group, y.group, intercept=FALSE, nfolds=NFOLDS)

        coefs <- coef(cv.rq.model)
        cat("nonzero coefs\n")
        print(coefs[coefs!=0])
        cat("\n")
        #cat("all coefs\n")
        #print(coefs)
        #cat("\n")

        # evaluate the model predictions 

        preds.zero  <- 0
        preds.median<- median(y)
        preds.cvrq  <- predict(cv.rq.model, newx=x)[,1]

        err.zero    <- sum(abs(y - preds.zero))
        err.median  <- sum(abs(y - preds.median))
        err.cvrq    <- sum(abs(y - preds.cvrq))

        errs <- errs + c(err.zero, err.median, err.cvrq)
        cat("TOTERROR group: ", group, " zero/median/cvrq: ")
        print(errs)

    }
}


