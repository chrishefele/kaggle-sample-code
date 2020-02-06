# usage:  Rscript model.R <clfrf | clfgbm> <plotfile> <submissionfile>

library('randomForest')
library('gbm')

TRAIN_FEATURES  <- '../features/leakage_features_train.csv'
TEST_FEATURES   <- '../features/leakage_features_test.csv'
RND_SEED        <- 12345678

rf_common <- function(x, y, xnew, response_type) {
    NTREE          <- 500  # TODO tune this? 
    TREE_NODE_SIZE <- 30
    cat(paste("Creating Random Forest using: ", as.character(NTREE)," trees\n"))
    rf <- randomForest(x, y, ntree=NTREE ,nodesize=TREE_NODE_SIZE,
                       importance=TRUE ,do.trace=TRUE) 
    print("ERRORS")
    print(rf$mse)
    print(paste("MINERROR:", as.character(min(rf$mse))))
    print("VARIABLE IMPORTANCE")
    rf.imp <- as.data.frame(importance(rf))
    print(rf.imp)
    print("SORTED VARIABLE IMPORTANCE")
    sort.field <- ifelse(rf$type=='classification', "MeanDecreaseAccuracy", "%IncMSE")
    rf.imp.sort <- rf.imp[ order(rf.imp[[sort.field]], decreasing=TRUE) , ]
    print(rf.imp.sort)
    summary(rf)
    plot(rf)

    preds <- predict(rf, xnew, type=response_type)
    if(rf$type == 'regression')     { return(preds)   }
    if(rf$type == 'classification') { return(as.data.frame(preds)[["1"]]) }
}

gbm_common <- function(x, y, xnew, dist.family, ntrees=2100  ) {
    GBM_NTREES    = ntrees   
    GBM_SHRINKAGE = 0.05
    GBM_DEPTH     = 4     
    GBM_MINOBS    = 50
    GBM_TRAIN_FRACTION = 1.0  # 1 for no CV, <1 for some CV

    cat(paste('Creating GBM model using:', as.character(ntrees),'trees\n'))

    GBM_model <- gbm.fit(x = x, y = y
                ,distribution = dist.family,  n.trees = GBM_NTREES
                ,shrinkage = GBM_SHRINKAGE,   interaction.depth = GBM_DEPTH
                ,n.minobsinnode = GBM_MINOBS, verbose = TRUE
                ,train.fraction = GBM_TRAIN_FRACTION )

    #list variable importance
    print(summary(GBM_model, GBM_NTREES))

    # estimates optimum number of iterations & creates plots 
    nopt <- gbm.perf(GBM_model, method='OOB') 
    cat(paste('Optimum number of GBM iterations via OOB :', as.character(nopt),'\n'))
    nopt <- gbm.perf(GBM_model, method='test') 
    cat(paste('Optimum number of GBM iterations via TEST:', as.character(nopt),'\n'))

    preds <- predict.gbm( object=GBM_model, newdata=xnew, 
                          type='response',  n.trees=GBM_NTREES )
    return(preds)
}

make_predictions <- function(X, Y, Xnew, model_type) {
    if(model_type=='clfrf')  { preds <- rf_common( X, factor(Y), Xnew, 'prob') } 
    if(model_type=='clfgbm') { preds <- gbm_common(X,        Y , Xnew, 'bernoulli') } 
    return(preds)
}

echoprint <- function(a, tag) { 
    cat(tag,' = ',a,'\n') 
    return(a)
}

main <- function() {
    starttime <- proc.time() 
    set.seed(RND_SEED)
    cat('\n*** Whale Redux Modeling ***\n\n')

    args            <- commandArgs(TRUE)
    model_type      <- echoprint(args[1],  'model_type     ')
    plot_file       <- echoprint(args[2],  'plot_file      ') 
    submission_file <- echoprint(args[3],  'submission_file') 

    train_features  <- read.csv(TRAIN_FEATURES)
    train_target    <- train_features$whale_heard
    train_features$whale_heard <- NULL
    train_clips     <- train_features$clip
    train_features$clip <- NULL

    test_features   <- read.csv(TEST_FEATURES)
    #
    test_features$whale_heard <- NULL
    test_clips      <- test_features$clip
    test_features$clip <- NULL

    pdf(file = plot_file)

    X    <- train_features
    Y    <- train_target
    Xnew <- test_features

    cat('Making predictions...\n')
    predictions <- make_predictions(X, Y, Xnew, model_type)

    submission <- data.frame(clip=test_clips, probability=predictions)
    cat('\nWriting predictions file...\n')
    write.csv(submission, file=submission_file, row.names=FALSE, quote=FALSE)
    cat(paste('Wrote submission to :', submission_file,'\n'))

    elapsedtime <- proc.time() - starttime
    print(elapsedtime)
    cat("\nDone.\n")
}

main()


