# worst.R 

#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_1_T1_20_8_.csv
#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_1_T3_20_8_.csv
#/home/chefele/Dropbox/essay/submissions/real/RAW_CV_LG_SM_10_8_.csv
#
# "essay_id"    "actual"      "prediction"  "essay_settA"
# essay_id,actual,prediction,essay_settA
# 1,8,8.41722043963499,1
# 2,9,9.1250817907871,1
#

NWORST <- 25

FNAME <- "RAW_CV_LG_SM_10_8_.csv"
fdat  <- read.csv(FNAME)

train <- read.delim("../../download/release_3/training_set_rel3.tsv", quote="")

disagrees        <- abs(train$rater1_domain1 - train$rater2_domain1)
names(disagrees) <- train$essay_id 

# for sets 1,7,8, score is sum of the rater scores; otherwise, use mean of the 2 rater scores
mask                 <- train$essay_set==1 | train$essay_set==7  | train$essay_set==8
actual_middle        <- (train$rater1_domain1       + train$rater2_domain1      )/2.0
actual_middle[mask]  <- (train$rater1_domain1[mask] + train$rater2_domain1[mask])  
names(actual_middle) <- train$essay_id

essay_text       <- train$essay
names(essay_text)<- train$essay_id

fdat$disagrees   <- as.vector(disagrees[as.character(fdat$essay_id)])
fdat$actual_middle<-as.vector(actual_middle[as.character(fdat$essay_id)])
fdat$sqerr       <- as.vector((fdat$prediction - fdat$actual       )^2)
fdat$sqerr_middle<- as.vector((fdat$prediction - fdat$actual_middle)^2)
fdat$essay_text  <- as.vector(essay_text[as.character(fdat$essay_id)])

for(eset in unique(fdat$essay_settA)) {
    dat      <- fdat[fdat$essay_settA==eset,]
    dat.sort <- dat[ order(dat$sqerr_middle, decreasing=TRUE) ,] 
    # print(head(dat.sort ,10))
    outstring <- paste( "\n\n\n",
                        "essay_id:",    as.character(dat.sort$essay_id),
                        "essay_settA:", as.character(dat.sort$essay_settA),
                        "prediction:",  as.character(dat.sort$prediction),
                        "actual_middle:",as.character(dat.sort$actual_middle),
                        "sqerr_middle:",as.character(dat.sort$sqerr_middle),
                        "disagrees:",   as.character(dat.sort$disagrees),
                        "\n\n",         dat.sort$essay_text
                       )

    outfile <- paste("worst_set_",eset,".txt",sep="")
    cat(outstring[1:NWORST], file=outfile)
}

