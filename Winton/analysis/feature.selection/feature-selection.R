# feature-selection.R
#
# Runs a random forest and glmnet models on input features
# for the purpose of feature selection 
#
# usage:  cat models.R | R --vanilla | tee feature-selection.log
#
# Chris Hefele, 11/2015
#

library('randomForest')
library('glmnet')
library('caret')
library('Boruta')

# -------------------- Constants / parameters

FEATURES_X_FILE  <- "../data/train.RData"
PLOT_FILE        <- 'feature-selection.pdf'
pdf(file=PLOT_FILE)

NTREE          <- 250 # 500 is about 0.15% better (in %IncMSE) than 250
TREE_NODE_SIZE <-  20 # min number of data points required at leaf nodes 
RND_SEED <- 12345678
set.seed(RND_SEED)

# -------------------- 

args<-commandArgs(TRUE)

# -------------------- Create X & Y variables for modeling

cat("Reading X features from: ", FEATURES_X_FILE,"\n")
x <- readRDS(file=FEATURES_X_FILE)
x[is.na(x)] <- 0
cat("X features have the following dimensions: ", dim(x),"\n")

target.col <- args[1]
cat("target column: ", target.col, "\n")
stopifnot(target.col %in% c("Ret_180","Ret_PlusOne","Ret_PlusTwo"))
y  <- x[,target.col]

del.cols <- c("Ret_180","Ret_PlusOne","Ret_PlusTwo",
              "Weight_Intraday","Weight_Daily")
for(del.col in del.cols) { 
    x[,del.col] <- NULL 
} 

# collapse many intraday returns into just one sum 
ret.sum <- 0
for(sum.col in paste("Ret", c(2:179), sep="_")) { 
    ret.sum <- ret.sum + x[,sum.col] 
    x[,sum.col] <- NULL
} 
x[,"Ret_2_179_Sum"] <- ret.sum

# add random variables
for(rand.col in paste("Rand", c(1:20), sep="_")) {
    x[,rand.col] <- rnorm(nrow(x))
}

cat("Head of X\n")
print(head(x))

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

