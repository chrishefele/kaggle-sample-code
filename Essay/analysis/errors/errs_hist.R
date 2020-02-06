
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

pdf(file="errs_hist.pdf")

for(eset in unique(fdat$essay_settA)) {
    tag <- paste("essay_set:", eset)
    print(tag)

    dat <- fdat[fdat$essay_settA==eset,]

    errs <- (dat$prediction - dat$actual)

    hist(errs, 100, main=paste("Histogram of",tag))
}



