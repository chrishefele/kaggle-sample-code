# interset.R
#
# Runs a random forest to explore interset predictions as features
#
# usage:  cat interset.R | R --vanilla --args <features_file>  

library('randomForest')

TRAINING_FILE <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
FEATURES_FILE <- commandArgs( trailingOnly=TRUE )[1] # features derived from training data

NTREE          <- 50  # TODO:  ****  CHANGE THIS TO 500
TREE_NODE_SIZE <- 20
RND_SEED <- 12345678
set.seed(RND_SEED)

features   <- read.csv(FEATURES_FILE)
features   <- features[features$sett==1,] # pick out training set from Phil's formatted data
features["domain1_score"] <- NULL  #...and remove the answers so the RF doesn't see them :)
features["domain2_score"] <- NULL
write.csv(features, file="../data/rf_input_features.training.csv", quote=FALSE, row.names=FALSE)

training   <- read.delim(TRAINING_FILE, quote="")

essay_sets <- sort(unique(features$essay_set))

# make all the rf models for all the essay sets
rf.models <- list()
for(essay_set in essay_sets) {
    print(paste("Making RF model for essay set:",essay_set))
    x  <- features[features$essay_set == essay_set,]
    y  <- training[training$essay_set == essay_set, 'domain1_score']
    rf <- randomForest(x, y, ntree=NTREE, nodesize=TREE_NODE_SIZE, importance=TRUE, do.trace=TRUE) 
    rf.models[[as.character(essay_set)]] <- rf
}

# now evaluate the models across all essay sets
for(essay_set in essay_sets) {

    print(paste("Making predictions for essay set:",essay_set))
    x  <- features[features$essay_set == essay_set,]
    y  <- training[training$essay_set == essay_set, 'domain1_score']
    ypreds <- data.frame(dummy=1:nrow(x))

    for(model_set in essay_sets) {
        rf.model <- rf.models[[as.character(model_set)]]
        tag <- paste("rf_model_set_",model_set,sep="")
        ypreds[,tag]  <- predict(rf.model, x)
    }
    ypreds$dummy <- NULL

    fname <- paste("../results/rf_essay_set",essay_set,".training.csv",sep="")
    write.csv(ypreds, file=fname, quote=FALSE, row.names=FALSE)

    print(paste("correlations for essay_set:",essay_set))
    cors <- cor(y, ypreds, method="pearson")
    print(cors)
}

