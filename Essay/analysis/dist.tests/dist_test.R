
# Can you look at the raw score distributions of the LB and CV files by essay set.

# essay/submissions/real/RAW_CV_LG_SM_10_8_.csv   # real values ; cross validation
# essay/submissions/real/RAW_LB_LG_SM_10_8_.csv   # real values ; leaderboard 

#==> RAW_CV_LG_SM_10_8_.csv <==
#essay_id,actual,prediction,essay_settA
#1,8,8.41722043963499,1
#2,9,9.1250817907871,1

#==> RAW_LB_LG_SM_10_8_.csv <==
#prediction_id,essay_id,essay_set,essay_weight,prediction,essay_settA
#1788,1788,1,1,7.64130792408858,1
#1789,1789,1,1,7.93516872567152,1

dat.cv <- read.csv("RAW_CV_LG_SM_10_8_.csv")   # real values ; cross validation
dat.lb <- read.csv("RAW_LB_LG_SM_10_8_.csv")   # real values ; leaderboard 

print(table(dat.cv$essay_settA))
print(table(dat.lb$essay_settA))

essay_sets <- sort(intersect(unique(dat.cv$essay_settA), unique(dat.lb$essay_settA)))

for(eset in essay_sets) {
    samp1 <- sort(dat.cv[dat.cv$essay_settA==eset, "prediction"])
    samp2 <- sort(dat.lb[dat.lb$essay_settA==eset, "prediction"])
    print(eset)
    print( ks.test(samp1,samp2) )
    lens1 <- (1:length(samp1)) / length(samp1)
    lens2 <- (1:length(samp2)) / length(samp2)
    plot.title <- paste("essay_set:", eset)
    plot( samp1, lens1, type="l", main=plot.title, xlab="Predicted Score", ylab="Cumulative distribution")
    lines(samp2, lens2 )
}



