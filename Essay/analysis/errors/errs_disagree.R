

#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_1_T1_20_8_.csv
#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_1_T3_20_8_.csv
#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_LG_SM_10_8_.csv
#
# "essay_id"    "actual"      "prediction"  "essay_settA"
# essay_id,actual,prediction,essay_settA
# 1,8,8.41722043963499,1
# 2,9,9.1250817907871,1
#

FNAME <- "RAW_CV_LG_SM_10_8_.csv"
fdat  <- read.csv(FNAME)

train <- read.delim("../../download/release_3/training_set_rel3.tsv", quote="")
disagrees        <- abs(train$rater1_domain1 - train$rater2_domain1)
names(disagrees) <- train$essay_id 

actual_middle        <- (train$rater1_domain1 + train$rater2_domain1)/2.0
names(actual_middle) <- train$essay_id

fdat$disagrees <- as.vector(disagrees[as.character(fdat$essay_id)])
fdat$actual_middle<-as.vector(actual_middle[as.character(fdat$essay_id)])
fdat$sqerr       <- as.vector((fdat$prediction - fdat$actual       )^2)
fdat$sqerr_middle<- as.vector((fdat$prediction - fdat$actual_middle)^2)

#print(fdat)

for(eset in unique(fdat$essay_settA)) {
    tag <- paste("essay_set:", eset)
    print(tag)
    dat <- fdat[fdat$essay_settA==eset,]

    ds.name <- names(table(dat$disagrees))
    ds.count<- as.vector(table(dat$disagrees))
    ds.mean <- as.vector(tapply(dat$sqerr_middle, dat$disagrees, mean))
    ds.sqerr<- as.vector(tapply(dat$sqerr_middle, dat$disagrees, sum))

    ds <- data.frame(essay_set=eset, score_delta=ds.name, score_delta_count=ds.count, 
                     sqerr_mean=ds.mean, sqerr_fraction=ds.sqerr/sum(ds.sqerr) )
    print(ds)
}

