
#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_1_T1_20_8_.csv
#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_1_T3_20_8_.csv
#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_LG_SM_10_8_.csv
#
# "essay_id"    "actual"      "prediction"  "essay_settA"
# essay_id,actual,prediction,essay_settA
# 1,8,8.41722043963499,1
# 2,9,9.1250817907871,1
#

library("irr")

FNAME <- "RAW_CV_LG_SM_10_8_.csv"
fdat  <- read.csv(FNAME)

train <- read.delim("../../download/release_3/training_set_rel3.tsv", quote="")

for(eset in unique(fdat$essay_settA)) {

    tag <- paste("essay_set:", eset)
    print(tag)
    dat <- fdat[fdat$essay_settA==eset,]

    actual      <-         dat$actual
    preds.upper <- ceiling(dat$prediction   )
    preds.round <- round(  dat$prediction, 0)

    k1    <- kappa2(data.frame(a=actual, b=preds.upper), weight="squared")$value
    nerr1 <- sum(actual==preds.upper)

    k2    <- kappa2(data.frame(a=actual, b=preds.round), weight="squared")$value
    nerr2 <- sum(actual==preds.round)

    kappa.slope <- (k2-k1) / (nerr1-nerr2)
    print(0.0010/kappa.slope)

}






