pdf(file="uniq_length.pdf")

TRAIN      <- "/home/chefele/Essay/download/release_3/training_set_rel3.tsv"
FEATURES   <- "/home/chefele/Essay/xfeatures/xfeatures.training.csv"

train      <- read.delim(TRAIN,quote="")
feat       <- read.csv(FEATURES)
feat$score <- train$rater1_domain1 

feat    <- feat[feat$essay_set == 1,]



lenwords <-   feat$CH_nwords
uniqwords <-  feat$CH_numUniqWords
xmax <- max(lenwords)
ymax <- max(uniqwords)
plot(lenwords, uniqwords, xlab="length in words", ylab="unique words", type="p", xlim=c(0,xmax), ylim=c(0,ymax))

for(score in unique(feat$score)) {
    df <- feat[feat$score == score,]
    lenwords <-   df$CH_nwords
    uniqwords <-  df$CH_numUniqWords
    plot(lenwords, uniqwords, xlab="length in words", ylab="unique words", type="p", xlim=c(0,xmax), ylim=c(0,ymax))
}

