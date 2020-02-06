
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

pdf(file="errs_hists.pdf")

for(eset in sort(unique(fdat$essay_settA))) {
    dat <- fdat[fdat$essay_settA==eset,]
    for(score in sort(unique(dat$actual))) {
        tag <- paste("Predictions Histogram for essay_set:", eset,"actual_score:",score)
        print(tag)
        dat_score <- dat[dat$actual==score,]
        hist(dat_score$prediction, 20, main=tag, xlab="Prediction")
        abline(v = as.integer(score), col = "red")
    }
}

