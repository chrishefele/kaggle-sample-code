# try_ord_logit.R
#
# Runs a ordered logit, random forest and linear regression to see which works better
#
# usage:  cat try_ord_logit.R | R --vanilla 

library('randomForest')
library('glmnet')

pdf(file="try_ord_logit.pdf")
TRAINING_FILE <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
#FEATURES_FILE <- "/home/chefele/Essay/xfeatures/results/xfeatures.training.csv"
FEATURES_FILE <- "/home/chefele/Essay/ordlogit/data/all_features_reduced.csv"

NTREE         <- 500
TREE_NODE_SIZE <- 20

# ---------------

namesFilter <- function(all_names) { # return only names with specified prefixes
    all_names[c( grep("CH_",all_names), grep("BY_",all_names), grep("EJ_",all_names), 
                 grep("WC_",all_names), grep("PB_",all_names), grep("essay_set",all_names) )]
}

# ---- read in the data...

# the following is used for xfeatures.training.csv only 
# features   <- read.csv(FEATURES_FILE)  

# the following extracts features from the all_features_reduced.csv file
fin        <- read.csv(FEATURES_FILE)
features   <- fin[ fin$sett==1, namesFilter(names(fin)) ]

training   <- read.delim(TRAINING_FILE, quote="")

# ---- iterate through the essay sets 

essay_sets <- sort(unique(features$essay_set))
for(essay_set in essay_sets) {

    # select data for just one particular essay set
    print(paste("Starting on essay set:",as.character(essay_set)))
    x  <- features[features$essay_set == essay_set,]
    y  <- training[training$essay_set == essay_set, 'domain1_score']
    
    # --------------- first, fit an ordinal logit regression

    # get cumulative counts of each score level, and total number of scores (essays)
    ccounts <- data.frame(ccount=cumsum(table(y)))
    csum    <- sum(table(y))
    yc <- as.character(y)

    # form matrix of cumulative counts above and below-or-equal-to each score level 
    # this is what is needed by glmnet for ordered logit 
    belows <-        ccounts[yc,'ccount'] # actually, below or equal to...
    aboves <- csum - ccounts[yc,'ccount']
    yp <- as.matrix( cbind(aboves, belows) )
    xm <- as.matrix(x)
    tenfold_ids <- 1:nrow(xm) %% 10 + 1  # use same CV folds for both fits below

    print("Fitting ordered logit model...")
    # logistic regression on cumulative probs of ordered classes
    ordlogit.cv.fit <- cv.glmnet(xm, yp, family="binomial", foldid=tenfold_ids) 
    ypred.ordlogit  <- predict(ordlogit.cv.fit, xm, type="response")
    plot(ordlogit.cv.fit, main=paste("Ordinal Logit Regression, set:", essay_set))
    print(coef(ordlogit.cv.fit))  

    # ---------- next fit a linear regression 

    print("Fitting linear regression model...")
    linreg.cv.fit <- cv.glmnet(xm, y, family="gaussian", foldid=tenfold_ids) # linear regression
    ypred.linreg <- predict(linreg.cv.fit, xm, type="response")
    plot(linreg.cv.fit, main=paste("Linear Regression, set:", essay_set))
    print(coef(linreg.cv.fit))  

    # ---------- now fit an RF
    if(FALSE) {
        print("Fitting random forest model...")
        rf.fit <- randomForest(xm, y, ntree=NTREE, nodesize=TREE_NODE_SIZE, importance=TRUE, do.trace=FALSE) 
        ypred.rf <- predict(rf.fit, xm, type="response")

        # print variable importances in alphabetical order & importance order
        rf.imp <- as.data.frame(importance(rf.fit))
        print(rf.imp)
        sort.field <- "%IncMSE"   # other option is: "IncNodePurity"
        rf.imp.sort <- rf.imp[ order(rf.imp[[sort.field]], decreasing=TRUE) , ]
        print(paste("VARIABLE IMPORTANCE FOR ESSAY SET:",as.character(essay_set)))
        print(rf.imp.sort)
    } 
        

     
    # ---------- compare model performance
    
    cor.ordlogit <- as.character(cor(y, ypred.ordlogit, method="spearman"))
    #cor.rf       <- as.character(cor(y, ypred.rf,       method="spearman" ))
    cor.linreg   <- as.character(cor(y, ypred.linreg,   method="spearman" ))
    #print(paste("RankCorr vs Score for essay_set", essay_set,"OrdLogit:", cor.ordlogit, "RF:", cor.rf, "LinReg:", cor.linreg))
    print(paste("RankCorr vs Score for essay_set", essay_set,"OrdLogit:", cor.ordlogit, "LinReg:", cor.linreg))
    # note: rank correlation is used (rather than 'regular' correlation) 
    # because ordinal logit is nonlinear vs features, and on [0,1] scale; 
    # RF predicts actual scores. 
    
    cor.ordlogit <- as.character(cor(y, ypred.ordlogit, method="pearson" ))
    # cor.rf       <- as.character(cor(y, ypred.rf,       method="pearson" ))
    cor.linreg   <- as.character(cor(y, ypred.linreg,   method="pearson" ))
    #print(paste("Corr vs Score for essay_set", essay_set,"OrdLogit:", cor.ordlogit, "RF:", cor.rf, "LinReg:", cor.linreg))
    print(paste("PearsonCorr vs Score for essay_set", essay_set,"OrdLogit:", cor.ordlogit, "LinReg:", cor.linreg))

}


