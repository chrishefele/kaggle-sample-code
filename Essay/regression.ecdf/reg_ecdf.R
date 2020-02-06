# reg_ecdf.R
#
# usage:  cat reg_ecdf.R | R --vanilla --args <features_file>  

library('glmnet')

TRAINING_FILE <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
FEATURES_FILE <- commandArgs( trailingOnly=TRUE )[1] # features derived from training data

RND_SEED <- 12345678

features   <- read.csv(FEATURES_FILE)
training   <- read.delim(TRAINING_FILE, quote="")

essay_sets <- sort(unique(features$essay_set))
for(essay_set in essay_sets) {

    print(essay_set)

    x   <- as.matrix(features[features$essay_set == essay_set,])
    xp  <-           features[features$essay_set == essay_set,]
    for(nm in names(xp)) {
        xp[,nm] <- ecdf(xp[,nm])(xp[,nm]) # convert to percentiles
    }
    xp <- as.matrix(xp)

    x <- x  # or x<-xp or x<-x 
    y  <- as.vector(training[training$essay_set == essay_set, 'domain1_score'])

    set.seed(RND_SEED)
    fit <- cv.glmnet(x, y, family="gaussian")
    newy <- predict(fit,newx=x)
    sqerr <- sum((newy-y)^2)
    print(paste("essay_set:", as.character(essay_set),"squared_error:",as.character(sqerr)))

    print(fit)
    plot(fit, main=essay_set)
    print(coef(fit))

}


