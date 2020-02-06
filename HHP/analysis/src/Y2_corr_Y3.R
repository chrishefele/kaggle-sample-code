# Measure the correlation between Y2 and Y3 DIH values 

library(Kendall)

DaysInHospital.Y2 <- read.csv("hhp2data/DaysInHospital_Y2.csv")
DaysInHospital.Y3 <- read.csv("hhp2data/DaysInHospital_Y3.csv")

m  <- intersect(DaysInHospital.Y2$MemberID,DaysInHospital.Y3$MemberID)
ix <- match(m,DaysInHospital.Y2$MemberID)
jx <- match(m,DaysInHospital.Y3$MemberID)
table(DaysInHospital.Y2$DaysInHospital[ix],DaysInHospital.Y3$DaysInHospital[jx])

Kendall(DaysInHospital.Y2$DaysInHospital[ix],DaysInHospital.Y3$DaysInHospital[jx])
cor(    DaysInHospital.Y2$DaysInHospital[ix],DaysInHospital.Y3$DaysInHospital[jx])

length(m)
length(DaysInHospital.Y2)
length(DaysInHospital.Y3)


