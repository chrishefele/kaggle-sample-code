# Baseline scores for Heritage Health Prize
# by Chris Hefele

DATA_PATH <- "/home/chefele/HHP/download/HHP_release1/"

# ==> DayInHospital_Y2.csv <== memberid,DaysInHospital_Y2
dih     <- read.csv(paste(DATA_PATH,"DayInHospital_Y2.csv", sep=""))

# ==> Members_Y1.csv <== MemberID,sex,AgeAtFirstClaim
members <- read.csv(paste(DATA_PATH,"Members_Y1.csv", sep=""))

eps.score <- function(p,a) { sqrt(mean((log(p+1)-log(a+1))^2)) }

ln1mean <- function(x) { exp(mean(log(x+1)))-1 } 


mean.DIH.by.sex <- tapply(dih$DaysInHospital_Y2, members$sex, mean)
mean.DIH.by.age <- tapply(dih$DaysInHospital_Y2, members$AgeAtFirstClaim, mean)

barplot(mean.DIH.by.sex, ylab="Mean DaysInHospital", main="Mean DaysInHospital vs Sex")
barplot(mean.DIH.by.age, ylab="Mean DaysInHospital", main="Mean DaysInHospital vs Age")



exp.mean.log.DIH.by.sex <- exp( tapply(log(dih$DaysInHospital_Y2+1), members$sex, mean) ) -1 
exp.mean.log.DIH.by.age <- exp( tapply(log(dih$DaysInHospital_Y2+1), members$AgeAtFirstClaim, mean) ) -1 

barplot(exp.mean.log.DIH.by.sex, ylab="exp(Mean(Log(DaysInHospital+1))-1", main="LogMean DaysInHospital vs Sex")
barplot(exp.mean.log.DIH.by.age, ylab="exp(Mean(Log(DaysInHospital+1))-1", main="LogMean DaysInHospital vs Age")


mean.DIH.by.sex.age <- tapply( dih$DaysInHospital_Y2, list(as.factor(members$sex),as.factor(members$AgeAtFirstClaim)), mean)
mean.DIH.by.sex.age
barplot(mean.DIH.by.sex.age)

mean.DIH.by.sex.age <- tapply( dih$DaysInHospital_Y2, list(as.factor(members$sex),as.factor(members$AgeAtFirstClaim)), ln1mean)
mean.DIH.by.sex.age
barplot(mean.DIH.by.sex.age, main="Log+1 Mean of DaysInHospital by Age & Gender" )



