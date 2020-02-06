stsp <- read.csv("stsp3.csv")

me <- tapply( stsp$importance, stsp$feature , mean)
md <- tapply( stsp$importance, stsp$feature , median)
mx <- tapply( stsp$importance, stsp$feature , max)
mn <- tapply( stsp$importance, stsp$feature , min)

df <- cbind(me,md,mx,mn)
print(df)



