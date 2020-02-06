# CustID, DateMatches, SpendMatches, DateSpendMatches
# 8, 0, 0, 0
# 159, 3, 3, 1

m <- read.csv("cum3.csv")

fac <- as.integer( 10 * (m$CustID-1) / max(m$CustID) ) 
m$Bin <- fac

dateSpendMatches <- c(0, diff( m$DateSpendMatches ) )
dateMatches      <- c(0, diff( m$DateMatches ) )
spendMatches     <- c(0, diff( m$SpendMatches ) )

plot(tapply( dateSpendMatches, fac, mean ), type="b", main="%DateSpendMatches by CustID Decile",xlab="CustID Decile",ylab="%Matches")
plot(tapply( dateMatches, fac, mean ), type="b", main="%DateMatches by CustID Decile",xlab="CustID Decile",ylab="%Matches")
plot(tapply( spendMatches, fac, mean ), type="b", main="%SpendMatches by CustID Decile",xlab="CustID Decile",ylab="%Matches")


tapply( dateSpendMatches, fac, mean )
tapply( dateMatches, fac, mean )
tapply( spendMatches, fac, mean )

plot(tapply( m$Bin,  fac, length))
plot(tapply( m$Bin,  fac, length) , type="b", main="Entries in by CustID Decile", xlab="CustID Decile",ylab="#Entries")

