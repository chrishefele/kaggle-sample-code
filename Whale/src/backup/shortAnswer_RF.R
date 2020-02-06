# rf.R
#
# Runs a random forest for feature selection 
#
# usage:  cat rf.R | R --vanilla --args <features_file>  

library('randomForest')

TRAINING_FILE <- "/home/chefele/ShortAnswer/download/train_rel_2.tsv"
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
    y1 <- training[training$EssaySet  == essay_set, 'Score1']
    y2 <- training[training$EssaySet  == essay_set, 'Score2']
    y12<- (y1+y2)/2.0 

    # NOTE:   change y variable to train on y1, or y12, depending on what you want
    rf <- randomForest(x, y1 , ntree=NTREE, nodesize=TREE_NODE_SIZE, importance=TRUE, do.trace=TRUE) 

    print("ERRORS")
    print(rf$mse)
    print(paste("ESSAY","SET:", as.character(essay_set), "TRAINING_RMSE:", as.character(min(rf$mse))))

    preds <- predict(rf, x)
    y1err <- sqrt(mean((preds-y1)^2))
    print(paste("ESSAY","SET:", as.character(essay_set), "SCORE1_RMSE:", as.character(y1err)))

    print(paste("VARIABLE IMPORTANCE FOR ESSAY SET:",as.character(essay_set)))
    rf.imp <- as.data.frame(importance(rf))
    print(rf.imp)

    print(paste("SORTED VARIABLE IMPORTANCE FOR ESSAY SET:",as.character(essay_set)))
    sort.field <- "%IncMSE"   # other option is: "IncNodePurity"
    rf.imp.sort <- rf.imp[ order(rf.imp[[sort.field]], decreasing=TRUE) , ]
    print(rf.imp.sort)

}


