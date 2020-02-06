# compares RF to quantileRF & SVD?
#
# usage:  cat <programname>.R | R --vanilla --args <features_file>  

library('randomForest')
library('e1071')
library('quantregForest')

TRAINING_FILE <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
FEATURES_FILE <- commandArgs( trailingOnly=TRUE )[1] # features derived from training data
NTREE         <- 50 # 500
TREE_NODE_SIZE <- 20
RND_SEED <- 12345678
set.seed(RND_SEED)

features   <- read.csv(FEATURES_FILE)
training   <- read.delim(TRAINING_FILE, quote="")

essay_sets <- sort(unique(features$essay_set))
for(essay_set in essay_sets) {

    cat(paste("starting set:",essay_set,"\n"))
    x  <- features[features$essay_set == essay_set,]
    y  <- training[training$essay_set == essay_set, 'domain1_score']

    rf  <- randomForest(  x, y, ntree=NTREE, nodesize=TREE_NODE_SIZE, importance=TRUE, do.trace=TRUE) 
    qrf <- quantregForest(x, y, ntree=NTREE, nodesize=TREE_NODE_SIZE)
    #svm.model <- svm(x=x, y=y, type='eps-regression',kernel='linear', cost=1, gamma=1e-04, cachesize=128,tolerance=1)

    rf.pred  <- predict(rf,  newdata=x)
    rf.pred.round <- round(rf.pred,0)
    qrf.pred <- predict(qrf, newdata=x, quantiles=c(0.5))[,1]
    #svm.pred <- predict(svm.model, newdata=x)

    rf.sqerr  <- sum((y- rf.pred)^2)
    rf.round.sqerr <- sum((y-rf.pred.round)^2)
    qrf.sqerr <- sum((y-qrf.pred)^2)
    #svm.sqerr <- sum((y-svm.pred)^2)

    cat("\n")
    print(paste(  "essay_set: ", as.character(essay_set), 
                  "rf_sqerr  :", as.character(rf.sqerr ), 
                  "rf_round_sqerr:", as.character(rf.round.sqerr),
                  "qrf_sqerr :", as.character(qrf.sqerr )
                  #"svm_sqerr :", as.character(qrf.sqerr ),
               )
         )
}



