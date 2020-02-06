library('irr')

data <- read.csv("RAW_CV_LG_SM_10_8_.csv")
data$iprediction <- round(data$prediction,0)
data$jprediction <- as.integer(data$prediction)
set1 <- data[data$essay_settA==1,]

print(unique(data$essay_settA))
print(nrow(set1))

kappa.diffs <- c()
for(i in 1:1000) {
    boot.rows <- sample(1:nrow(set1), nrow(set1), replace=TRUE)
    set1.boot <- set1[boot.rows,]
    ratings.a <- data.frame(rater1=set1.boot$iprediction, rater2=set1.boot$actual)
    ratings.b <- data.frame(rater1=set1.boot$jprediction, rater2=set1.boot$actual)
    kappa.a <- kappa2(ratings.a, weight="squared")
    kappa.b <- kappa2(ratings.b, weight="squared")
    #print(kappa$value)
    kappa.diffs <- c(kappa.a$value-kappa.b$value,kappa.diffs)
}
print(mean(kappa.diffs))
print(sd(kappa.diffs))
hist(kappa.diffs)


# "essay_id"    "actual"      "prediction"  "essay_settA"



