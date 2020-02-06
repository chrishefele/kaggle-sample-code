# model.R -- modeling code for HHP by C.Hefele 11/2012
#
# usage: Rscript model.R  <model_type> <preprocess> <DIH_min> 
#                         <train_features_file> <train_target_file> 
#                         <test_features_file>  <test_target_file> 
#                         <submission_file> <plotfile.pdf>
#
# <model_type> = regglm | regrf | reggbm | clfglm | clfrf | clfgbm | reggbm100
#                where prefix 'reg'=regression mode, 'clf'=classification mode
#                The classifier uses DIH>0 and DIH=0 as the 2 classes. 
# <preprocess> = binf | realf   (whether or not to 'binarize' the features 
#                               (so (x>0) ->1, 0 otherwise), or to use their real values
# <DIH_min>    = DIHge0 | DIHge1 (train only on members with >= 0 or 1 days-in-hospital)
#                Note: must use DIHge0  if any classifer picked as <model_type>
# 

library('glmnet')
library('randomForest')
library('gbm')

RND_SEED         <- 12345678
PROB_NONZERO_DIH <- 0.15    # approx probability of nonzero days-in-hospital

# Helper/utility functions

rmsle     <- function(p, a) { sqrt(mean((log(p+1)-log(a+1))^2)) }  #error function
log1plus  <- function(x)    { log(x+1) } # convert DIH to log-domain DIH
exp1minus <- function(x)    { exp(x)-1 } # convert log-domain DIH to DIH
morethan  <- function(x,x0) { 1*(x>x0) } 

newline   <- function()        { cat('\n') }
echoprint <- function(s, tag)  { cat(paste(tag,':', s,'\n')) ; s }
load.df   <- function(fname)   { load(fname); return(dframe) }
read.df   <- function(fn, tag) { 
    cat(paste('Reading:',tag,'from:',fn))
    dframe <- load.df(fn) 
    nr <- paste(as.character(nrow(dframe)), ' rows',sep='')
    nc <- paste(as.character(ncol(dframe)), ' cols',sep='')
    cat(paste(' (',nr,', ',nc,')\n',sep=''))
    return(dframe)
}

# core functions for predictions

glm_common <- function(x, y, xnew, dist.family ) {
    glm.fit <- cv.glmnet( as.matrix(x), y, family=dist.family) 
    print(coef(glm.fit))
    print(glm.fit)
    plot(glm.fit)
    preds <- predict(glm.fit, newx=as.matrix(xnew), type="response")
    preds <- as.data.frame(preds)[["1"]] 
    return(preds)
}

rf_common <- function(x, y, xnew, response_type) {
    NTREE          <- 250  # TODO make 500? Around 1.5min/tree
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

gbm_common <- function(x, y, xnew, dist.family, ntrees=500 ) {
    GBM_NTREES    = ntrees   # 500 optimal for features, 100 for stacking
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
    cat(paste('Optimum number of GBM interations OOB:', as.character(nopt),'\n'))
    nopt <- gbm.perf(GBM_model, method='test') 
    cat(paste('Optimum number of GBM interations TEST:', as.character(nopt),'\n'))

    preds <- predict.gbm( object=GBM_model, newdata=xnew, 
                          type='response',  n.trees=GBM_NTREES )
    return(preds)
}

make_predictions <- function(X, Y, Xnew, Ynew, model_type, DIH_min) {
    binY <- morethan(Y, 0) # binary version of DIH (1 if DIH>0, 0 otherwise)
    logY <- log1plus(Y)

    if(model_type=='regglm') { preds <- glm_common(log1plus(X), logY, log1plus(Xnew), 'gaussian') }
    if(model_type=='regrf')  { preds <- rf_common(          X,  logY,          Xnew,  'response') }
    if(model_type=='reggbm') { preds <- gbm_common(         X,  logY,          Xnew,  'gaussian') }

    if(model_type=='reggbm100') { preds <- gbm_common(      X,  logY,          Xnew,  'gaussian', 
                                                                                      ntrees=100) }

    if(model_type=='clfglm') { preds <- glm_common(X, factor(binY), Xnew, 'binomial') }
    if(model_type=='clfrf')  { preds <- rf_common( X, factor(binY), Xnew, 'prob') } 
    if(model_type=='clfgbm') { preds <- gbm_common(X,        binY , Xnew, 'bernoulli') } 

    print("Range of raw predictions on log(x+1) scale")
    print(range(preds))

    # If training on only ~15% of members with DIH>0, scale down predicted DIH
    # E(DIH) = p(DIH>0)*E(DIH|DIH>0) + p(DIH=0)*0 = p(DIH>0)*E(DIH|DIH>0)
    if(DIH_min>=1) { 
        preds  <- preds * PROB_NONZERO_DIH 
    }

    preds <- exp1minus(preds)
    preds <- pmin(15,  preds)
    preds <- pmax( 0,  preds)

    logerr <- log1plus(preds) - log1plus(Ynew)
    rmsle  <- sqrt(mean(logerr*logerr))
    cat(paste('RMSLE vs test set:', as.character(rmsle), '\n'))

    return(preds)
}

main <- function() {
    starttime <- proc.time() 
    set.seed(RND_SEED)

    cat('\n*** HHP Modeling ***\n\n')

    args            <- commandArgs(TRUE)
    model_type      <- echoprint(args[1],'model_type     ')
    preprocess      <- echoprint(args[2],'preprocess     ')
    DIH_subset      <- echoprint(args[3],'DIH_subset     ')

    submission_file <- echoprint(args[8],'submission_file') # NOTE out of arg sequence
    plot_file       <- echoprint(args[9],'plot_file      ') # NOTE out of arg sequence
    pdf(file = plot_file)
    newline()

    train_features  <- read.df( args[4], 'train_features ')
    train_target    <- read.df( args[5], 'train_target   ')    
    test_features   <- read.df( args[6], 'test_features  ')
    test_target     <- read.df( args[7], 'test_target    ')
    newline()

    # feature preprocessing 
    if(preprocess=='binf') {
        cat('Using BINARIZED version of features (not original values)\n\n')
        train_features <- morethan(train_features, 0)
        test_features  <- morethan(test_features,  0)
    } else {
        cat('Using ORIGINAL version of features (not binarized values)\n\n')
    }

    # Train only on data where DaysInHospital >= a value from the command line
    DIH_min <- ifelse(DIH_subset=='DIHge1', 1, 0)
    cat(paste('Training on members with DIH minimum of:',as.character(DIH_min),'\n'))
    mask <- train_target$DaysInHospital >= DIH_min
    train_features <- train_features[mask,]
    train_target   <- train_target[  mask,]
    echoprint( as.character(length(mask)),  'All DIH train rows')
    echoprint( as.character(sum(1*mask )),  'Min DIH train rows')
    newline()

    X    <- train_features
    Y    <- train_target$DaysInHospital
    Xnew <- test_features
    Ynew <- test_target$DaysInHospital

    cat('Making predictions...\n')
    predictions <- make_predictions(X, Y, Xnew, Ynew, model_type, DIH_min)
    submission <- data.frame( MemberID       = test_target$MemberID, 
                              DaysInHospital = predictions)
    cat('\nWriting predictions file...\n')
    write.csv(submission, file=submission_file, row.names=FALSE, quote=FALSE)
    cat(paste('Wrote submission to :', submission_file,'\n'))

    elapsedtime <- proc.time() - starttime
    print(elapsedtime)
    cat("\nDone.\n")
}

main()


