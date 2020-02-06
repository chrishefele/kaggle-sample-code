# predict-abs-Ret_PlusTwo
#
# Runs a random forest and glmnet models on input features
# for the purpose of feature selection 
#
# usage:  cat thisfile.R | R --vanilla | tee log.log 
#
# Chris Hefele, 12/2015
#

library('randomForest')
library('glmnet')
library('caret')
library('Boruta')

# -------------------- Constants / parameters

FEATURES_X_FILE  <- "../data/train.RData"
PLOT_FILE        <- 'predict-abs-Ret_PlusTwo.pdf'
pdf(file=PLOT_FILE)

NTREE          <- 250 
TREE_NODE_SIZE <-  20 # min number of data points required at leaf nodes 
RND_SEED <- 12345678
set.seed(RND_SEED)

# -------------------- Create X & Y variables for modeling

cat("Reading X features from: ", FEATURES_X_FILE,"\n")
x <- readRDS(file=FEATURES_X_FILE)
x[is.na(x)] <- 0
cat("X features have the following dimensions: ", dim(x),"\n")

target.col <- "Ret_PlusTwo"
cat("target column: ", target.col, "\n")
stopifnot(target.col %in% c("Ret_PlusOne","Ret_PlusTwo"))

y  <- abs(x[,target.col])  # NOTE: *** absolute value of return, NOT return

del.cols <- c("Id", "Ret_PlusOne","Ret_PlusTwo",
              "Weight_Intraday","Weight_Daily")
for(del.col in del.cols) { 
    x[,del.col] <- NULL 
} 

# create functions of all the intraday returns

intraday.cols           <- paste("Ret", c(2:180), sep="_")
ret.intraday            <- x[, intraday.cols]
for(i.col in intraday.cols) { x[,i.col] <- NULL } 

ret.intraday.sd         <- apply(ret.intraday, 1, sd)
ret.intraday.sum        <- apply(ret.intraday, 1, sum)
ret.intraday.sum.abs    <- apply(ret.intraday, 1, function(x) sum(abs(x)))
ret.intraday.median     <- apply(ret.intraday, 1, median)
ret.intraday.median.abs <- apply(ret.intraday, 1, function(x) median(abs(x)))
abs.ret.minusone         <- abs(x$Ret_MinusOne)
abs.ret.minustwo         <- abs(x$Ret_MinusTwo) 

intraday.features <- data.frame( 
                        ret.intraday.sd, 
                        ret.intraday.sum,       
                        ret.intraday.sum.abs, 
                        ret.intraday.median,  
                        ret.intraday.median.abs, 
                        abs.ret.minusone,        
                        abs.ret.minustwo
                    )

# create functions of some of the features

feature.cols.n  <- c(2,3,4,6,11,14,17,18,19,21,22,23,24,25)
feature.cols    <- paste("Feature", feature.cols.n, sep="_")
features <- data.frame(dummy=1:nrow(x))
for(f.col in feature.cols) {
    features[,paste("exp",    f.col, sep="")] <- exp( x[, f.col])
    features[,paste("expneg", f.col, sep="")] <- exp(-x[, f.col])
}
features$dummy <- NULL

# bring them all together...

x <- cbind(x, intraday.features, features)

# add random variables
for(rand.col in paste("Rand", c(1:20), sep="_")) {
    x[,rand.col] <- rnorm(nrow(x))
}

cat("Head of X\n")
print(head(x))


# -------------------- Simple correlations

cat("Simple correlations with Y\n")
y.df <- data.frame(y)
cors <- cor(x, y.df)
print(round( cors, digits=3))

# -------------------- Constant model

err <- y - mean(y)
mse <- mean(err^2)
cat("\n\nCONSTANT model MSE            : ", mse,     "\n")
cat(    "CONSTANT model MEAN prediction: ", mean(y), "\n")

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


# -------------------- Boruta feature selection 
 
if(TRUE) {

    boruta <- Boruta(x=x, y=y, maxRuns=100, doTrace=2, 
                      ntree=100, nodesize=20, do.trace=TRUE)
    print(boruta)
    cat("Boruta selected attributes:\n")
    boruta.selected <- getSelectedAttributes(boruta)
    print(boruta.selected)
    cat("Boruta selected and tentative attributes:\n")
    print(getSelectedAttributes(boruta, withTentative=FALSE))
    cat("Boruta stats:\n")
    print(attStats(boruta))
    cat("Boruta Importance History:\n")
    print(boruta$ImpHistory)
    plot(boruta)
}

# -------------------- Caret RandomForest model (used for "proper" CV)

if(TRUE) {

    rf.caret <- train(  
               x=x, y=y, method="rf", 
               ntree=100, nodesize=20, importance=TRUE, do.trace=TRUE,
               trControl=trainControl(method="boot", number=25, verboseIter=TRUE)
             )

    print(rf.caret)
    print(varImp(rf.caret))
    print(rf.caret$results)
    plot(rf.caret)

}

# -------------------- 

cat("\nDone.\n")

