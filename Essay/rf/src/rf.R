# rf.R
#
# Runs a random forest for feature selection 
#
# usage:  cat rf.R | R --vanilla --args <features_file>  

library('randomForest')

TRAINING_FILE <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
FEATURES_FILE <- commandArgs( trailingOnly=TRUE )[1] # features derived from training data
NTREE         <- 500
TREE_NODE_SIZE <- 20
RND_SEED <- 12345678
set.seed(RND_SEED)

features   <- read.csv(FEATURES_FILE)
training   <- read.delim(TRAINING_FILE, quote="")

essay_sets <- sort(unique(features$essay_set))
for(essay_set in essay_sets) {

    x  <- features[features$essay_set == essay_set,]
    y  <- training[training$essay_set == essay_set, 'domain1_score']
    rf <- randomForest(x, y, ntree=NTREE, nodesize=TREE_NODE_SIZE, importance=TRUE, do.trace=TRUE) 

    print("ERRORS")
    print(rf$mse)
    print(paste("ESSAY","SET:", as.character(essay_set), "MINERROR:", as.character(min(rf$mse))))

    print(paste("VARIABLE IMPORTANCE FOR ESSAY SET:",as.character(essay_set)))
    rf.imp <- as.data.frame(importance(rf))
    print(rf.imp)

    print(paste("SORTED VARIABLE IMPORTANCE FOR ESSAY SET:",as.character(essay_set)))
    sort.field <- "%IncMSE"   # other option is: "IncNodePurity"
    rf.imp.sort <- rf.imp[ order(rf.imp[[sort.field]], decreasing=TRUE) , ]
    print(rf.imp.sort)

}


