TRAIN      <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"

train      <- read.delim(TRAIN,quote="")

esets <- unique(train$essay_set)

for(eset in esets) {
    print(eset)
    train.eset <- train[train$essay_set==eset,]
    r1 <- train.eset$rater1_domain1
    r2 <- train.eset$rater2_domain1
    diffs <- table(abs(r1-r2))
    print( diffs / sum(diffs) ) 
}

