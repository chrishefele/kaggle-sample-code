library('irr')

TRAIN <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
train <- read.delim(TRAIN, quote="")

esets <- unique(train$essay_set)

for(eset in esets) {
    print(paste("essay_set:",eset))
    ratings.df <- train[ train$essay_set==eset, c("rater1_domain1", "rater2_domain1") ]
    print( kappa2(ratings.df, weight="squared") ) 
}

