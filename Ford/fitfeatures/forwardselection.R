library(caTools)
library(glmnet)

FIT_SAMPLES  <- 10000
LAMBDA <- "lambda.min"

best.auc.col <- function(datacols, target) {
    candidate.cols <- names(datacols)
    best.candidate.col <- c()
    best.candidate.auc <- 0 
    for(candidate.col in candidate.cols) {
            X.col <- as.matrix( datacols[ candidate.col ] )
            fit.mask <- sample(1:nrow(X.col), FIT_SAMPLES)
            X <- X.col[ fit.mask , ] 
            Y <- target[ fit.mask ]
            candidate.auc <- colAUC( X, Y , plotROC=FALSE)
            if(candidate.auc > best.candidate.auc) {
                best.candidate.col <- candidate.col
                best.candidate.auc <- candidate.auc 
            }
            print(  paste(candidate.col,"=",as.character(candidate.auc)))
    }
    print( paste("Best single-variable AUC column:",best.candidate.col) )
    return(best.candidate.col)
}


fw.feature.select <- function(datacols, target, num.to.select) {
    first.col <- best.auc.col(datacols,target)
    candidate.cols <- names(datacols)
    candidate.cols <- candidate.cols[ candidate.cols != first.col ] 
    picked.cols <- c(first.col)   
    last.best.candidate.auc <- 0   
    for(n in 2:num.to.select) {
        best.candidate.col <- c()
        best.candidate.auc <- 0.0
        for(candidate.col in candidate.cols) {
            X.matrix <- as.matrix( datacols[ c(picked.cols,candidate.col) ] )
            fit.mask <- sample(1:nrow(X.matrix), FIT_SAMPLES)
            X <- X.matrix[ fit.mask , ] 
            Y <- target[ fit.mask ]
            st<- system.time( 
                fit.train <- cv.glmnet(X, Y, type.measure="auc", family="binomial") )
            Y.predictions   <- predict(fit.train, newx=X, s=LAMBDA, type="response")
            candidate.auc <- colAUC( Y.predictions, Y , plotROC=FALSE)
            if(candidate.auc > best.candidate.auc) {
                best.candidate.col <- candidate.col
                best.candidate.auc <- candidate.auc
            }
            print(  paste(candidate.col,"=",as.character(candidate.auc)))
        }
        # if(best.candidate.auc > last.best.candidate.auc) {
        if(TRUE) { 
            last.best.candidate.auc <- best.candidate.auc
            picked.cols <- c(picked.cols, best.candidate.col)
            candidate.cols <- candidate.cols[candidate.cols!=best.candidate.col]
            print("PASS RESULTS:")
            print(paste("AUC:",as.character(best.candidate.auc) ))
            print(picked.cols)
        } else {
            print("No improvement this pass; terminating search")
            break
        }
    } 
    return(picked.cols)
}

# **********  MAIN 

train       <- read.csv("/home/chefele/Ford/download/fordTrain.csv")
features    <- read.csv("/home/chefele/Ford/mkfeatures/fordTrain.features.csv")

rslt <- fw.feature.select(features, train$IsAlert, 20)
print(rslt)

