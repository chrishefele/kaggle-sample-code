
TRAIN      <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"

pdf(file="acf.pdf")

train      <- read.delim(TRAIN,quote="")
esets <- unique(train$essay_set)

for(eset in esets) {
    print(eset)
    train.eset <- train[train$essay_set==eset,]
    scores <- train.eset$domain1_score
    results <- acf(scores, main=paste("essay_set", as.character(eset)))
    print(results$acf)
}

