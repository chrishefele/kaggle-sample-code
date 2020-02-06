
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
fdat$disagrees <- as.vector(disagrees[as.character(fdat$essay_id)])

print(names(fdat))
ESETS <- c("1","3","5","6") # essay sets where >1 pt disagreement leads to more sqerr
fdat <- fdat[as.character(fdat$essay_settA) %in% ESETS,]

excludes <- fdat[fdat$disagrees>1,"essay_id"]
print(excludes)
cat(paste(as.character(excludes),"\n"))


