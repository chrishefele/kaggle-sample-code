# Assemble a submission for the SemiSupervised Kaggle.com compeition
# CJH 10/11/2011
# Read in all the various feature files, run a classifier, and output a file for the SVM
#
# RUNTIME: 117minutes 
#

#------------------------------------------------------------------------------

BALANCE_DATA  <- TRUE # ****** flag to use data balancing in classifiers 

DIR_DOWNLOAD  <- "/home/chefele/SemiSupervised/download/competition_data/"
DIR_KMEANS    <- "/home/chefele/SemiSupervised/kmeans/data/"
DIR_DATA      <- "/home/chefele/SemiSupervised/data/data/"

TRAIN_ACTUALS <- paste(DIR_DOWNLOAD, "public_train.labels.dat", sep="")

TRAIN_KMEANS  <- paste(DIR_KMEANS,"full_kmeans.train.dense.dat",sep="") #del first col
TRAIN_ANALOG  <- paste(DIR_DATA,  "train_analog.csv",           sep="") 
TRAIN_BINARY  <- paste(DIR_DATA,  "bsvd_features_train.csv",    sep="") 

TEST_KMEANS   <- paste(DIR_KMEANS,"full_kmeans.test.dense.dat", sep="") # del first col
TEST_ANALOG   <- paste(DIR_DATA,  "test_analog.csv",            sep="") 
TEST_BINARY   <- paste(DIR_DATA,  "bsvd_features_test.csv",     sep="") 

FEATURES_OUT_TRAIN <- "features_for_svm_train.csv"
FEATURES_OUT_TEST  <- "features_for_svm_test.csv"

PLOT_FILE     <- "mk_features.pdf"
pdf(PLOT_FILE)

#------------------------------------------------------------------------------

library(glmnet) # for logistic 
library(e1071)  #for svd
library(randomForest) 
library(LiblineaR)  # for svd 
library(ROCR)

plotROC<- function(predictions, labels, plot.name) {
    # ROCR functions below
    plot(
        performance( 
            prediction(predictions,labels), measure = "tpr", x.measure = "fpr" 
        ), 
        main=plot.name
    )
}

calcAUC <- function(predictions, labels) {
    pred.tmp    <- prediction(predictions, labels) # ROCR function
    calc.AUC  <- performance(pred.tmp, "auc")@y.values[[1]] # ROCR function
    if(calc.AUC < 0.5) calc.AUC <- 1-calc.AUC
    return(calc.AUC) 
}

tagCols <- function(df, tag) { 
    names(df) <- paste(tag, names(df), sep="_")
    return(df)
}

# select variables with non-zero weights in a LR using L1 regularization
filterVars <- function(df) {
  df_out <- data.frame( 
    kmeans_V2 = df$kmeans_V2,
    kmeans_V6 = df$kmeans_V6, kmeans_V12 = df$kmeans_V12, kmeans_V14 = df$kmeans_V14,
    kmeans_V19 = df$kmeans_V19, kmeans_V21 = df$kmeans_V21, kmeans_V26 = df$kmeans_V26,
    kmeans_V31 = df$kmeans_V31, kmeans_V46 = df$kmeans_V46, kmeans_V48 = df$kmeans_V48,
    kmeans_V50 = df$kmeans_V50, kmeans_V53 = df$kmeans_V53, kmeans_V55 = df$kmeans_V55,
    kmeans_V59 = df$kmeans_V59, kmeans_V61 = df$kmeans_V61, kmeans_V72 = df$kmeans_V72,
    kmeans_V74 = df$kmeans_V74, kmeans_V77 = df$kmeans_V77, kmeans_V80 = df$kmeans_V80,
    kmeans_V82 = df$kmeans_V82, kmeans_V84 = df$kmeans_V84, kmeans_V85 = df$kmeans_V85,
    kmeans_V87 = df$kmeans_V87, kmeans_V90 = df$kmeans_V90, kmeans_V91 = df$kmeans_V91,
    kmeans_V97 = df$kmeans_V97,
    analog_V2 =  df$analog_V2,   analog_V4 = df$analog_V4, analog_V6 = df$analog_V6,
    analog_V8 =  df$analog_V8,   analog_V11 = df$analog_V11, analog_V13 = df$analog_V13,
    analog_V14 = df$analog_V14, analog_V16 = df$analog_V16, analog_V17 = df$analog_V17,
    analog_V19 = df$analog_V19, analog_V20 = df$analog_V20, analog_V21 = df$analog_V21,
    analog_V22 = df$analog_V22, analog_V28 = df$analog_V28, analog_V29 = df$analog_V29,
    analog_V30 = df$analog_V30, analog_V32 = df$analog_V32, analog_V33 = df$analog_V33,
    analog_V35 = df$analog_V35, analog_V37 = df$analog_V37, analog_V39 = df$analog_V39,
    analog_V40 = df$analog_V40, analog_V41 = df$analog_V41, analog_V42 = df$analog_V42,
    analog_V44 = df$analog_V44, analog_V45 = df$analog_V45, analog_V46 = df$analog_V46,
    binary_V2 =  df$binary_V2, binary_V3 = df$binary_V3, binary_V4 = df$binary_V4,
    binary_V6 =  df$binary_V6, binary_V8 = df$binary_V8, binary_V9 = df$binary_V9,
    binary_V10 = df$binary_V10, binary_V11 = df$binary_V11, binary_V12 = df$binary_V12,
    binary_V13 = df$binary_V13, binary_V14 = df$binary_V14, binary_V44 = df$binary_V44
  )
  return(df_out)
}


#------------------------------------------------------------------------------
# Read & prepare the datasets 

train_actuals <- as.factor( read.csv(TRAIN_ACTUALS, header=FALSE)$V1 ) 

train_kmeans  <- tagCols( read.csv(TRAIN_KMEANS, header=FALSE), "kmeans")
train_analog  <- tagCols( read.csv(TRAIN_ANALOG, header=FALSE), "analog")
train_binary  <- tagCols( read.csv(TRAIN_BINARY, header=FALSE), "binary")

test_kmeans   <- tagCols( read.csv(TEST_KMEANS,  header=FALSE), "kmeans")
test_analog   <- tagCols( read.csv(TEST_ANALOG,  header=FALSE), "analog")
test_binary   <- tagCols( read.csv(TEST_BINARY,  header=FALSE), "binary")

# delete first column, which is a constant 0 placeholder 
train_kmeans$kmeans_V1 <- NULL
test_kmeans$kmeans_V1  <- NULL

train <- as.matrix( cbind( train_kmeans, train_analog, train_binary ))
test  <- as.matrix( cbind( test_kmeans,  test_analog,  test_binary  ))

# FOR TESTING -- use a smaller sample
NSAMP <- 2000
train <- train[1:NSAMP,]
test  <- test[ 1:NSAMP,]
train_actuals <-train_actuals[1:NSAMP]

# constants used in data balancing
train_actuals_ones    <- table(train_actuals)["1"]
train_actuals_negones <- table(train_actuals)["-1"]


#------------------------------------------------------------------------------
# Fit various models to the datasets

# TODO  Make RF just a feature input to LR? Or input both to SVM? 
# TODO Scale data in the dataframe? 
# TODO: Use weights? 

# logistic regression on all features
fit.lr <- NULL
if(BALANCE_DATA) {
    wts <- as.vector(1.0*train_actuals)
    wts[train_actuals==-1] <- 1.0*train_actuals_ones/train_actuals_negones
    wts[train_actuals==1 ] <- 1.0
    system.time( fit.lr <- cv.glmnet(train, train_actuals, weights=wts, type.measure="auc", family="binomial") )

} else {
    system.time( fit.lr <- cv.glmnet(train, train_actuals,              type.measure="auc", family="binomial") )
}
print(BALANCE_DATA)
print(fit.lr)
summary(fit.lr)
coef(fit.lr)
#plot(fit.lr)

preds.test.lr  <- predict(fit.lr, newx=test , type="response")[,"1"] 
preds.train.lr <- predict(fit.lr, newx=train, type="response")[,"1"] 

aucStr <- as.character(calcAUC(preds.train.lr, train_actuals))
plotROC(preds.train.lr, train_actuals, paste("Logistic Regression ROC with AUC:", aucStr) )

# TODO: Use weights? 
# random forest on all features
fit.rf <- NULL
if(BALANCE_DATA) {
    counts <- table(train_actuals)
    class.wts <- c(  "-1"=(1.0*counts["1"]/counts["-1"]), "1"=1.0  )
    system.time( fit.rf <-randomForest(train, train_actuals, do.trace=TRUE, importance=TRUE, 
                                       ntree=500, nodesize=100, classwt=class.wts) )

} else {
    system.time( fit.rf <-randomForest(train, train_actuals, do.trace=TRUE, importance=TRUE, 
                                       ntree=500, nodesize=100) )
}

print(BALANCE_DATA)
print(fit.rf)
summary(fit.rf)
coef(fit.rf)
print(fit.rf$importance)
plot(fit.rf)
varImpPlot(fit.rf, sort=TRUE)

preds.test.rf  <- predict(fit.rf, newdata=test,  type="prob")[,"1"]
preds.train.rf <- predict(fit.rf, newdata=train, type="prob")[,"1"]

aucStr <- as.character(calcAUC(preds.train.rf, train_actuals))
plotROC(preds.train.rf, train_actuals, paste("Random Forest ROC with AUC:", aucStr) )

# write out the predictions 
train.out <- data.frame(rforest=preds.train.rf, logreg=preds.train.lr)
test.out  <- data.frame(rforest=preds.test.rf,  logreg=preds.test.lr )

write.csv(train.out, file=FEATURES_OUT_TRAIN, row.names=FALSE, col.names=TRUE, quote=FALSE)
write.csv(test.out,  file=FEATURES_OUT_TEST , row.names=FALSE, col.names=TRUE, quote=FALSE)

stop("Finished writing feature files")

# Now have to do svd below, seperately

#------------------------------------------------------------------------------


# system.time( fit.svm <-svm(train, train_actuals, kernel="linear",cost=1, probability=TRUE)

train_scaled<- scale(as.matrix(train), center=TRUE, scale=TRUE)
model_type <- 1
# 0 = L2 reg logistic regression
# 6 = L1 reg logistic regression
# 1 = L2 reg L2 loss SVM (dual)
# 2 = L2 reg L2 loss SVM (primal)
# 3 = L2 reg L1 loss SVM (dual)
# 5 = L1 reg L2 loss SVM

model <- LiblineaR(data=train_scaled, labels=train_actuals, type=model_type, cost=1, bias=TRUE, cross=0, verbose=TRUE)
predict_result <- predict(model, train_scaled, decisionValues=TRUE)
predvals<- predict_result$predictions

print("Training predvals AUC:")
print(calcAUC(predvals, train_actuals))

hist( predvals, main="Predicted SVM Values", 100)
auc <- calcAUC( predvals, train_actuals ) 
plot.title <- paste("PredValsSVM","AUC:",as.character(auc))
plotROC( predvals, train_actuals, plot.title )

# test_scaled<- scale(test, attr(train_scaled,"scaled:center"), attr(train_scaled,"scaled:scale"))

