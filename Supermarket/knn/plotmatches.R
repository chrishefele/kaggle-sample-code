# CustID, DateMatches, SpendMatches, DateSpendMatches
# 8, 0, 0, 0
# 159, 3, 3, 1

m <- read.csv("cum3.csv")
plot(m$CustID, m$DateSpendMatches, type="l")
plot(m$CustID, m$DateMatches, type="l")
plot(m$CustID, m$SpendMatches, type="l")

ExpectedDateSpendMatches <- max(m$DateSpendMatches) * 1.0 * m$CustID / max(m$CustID) 
ExpectedDateMatches  <- max(m$DateMatches) * 1.0 * m$CustID / max(m$CustID) 
ExpectedSpendMatches <- max(m$SpendMatches) * 1.0 * m$CustID / max(m$CustID) 

plot(m$CustID, m$DateSpendMatches - ExpectedDateSpendMatches, type="l")
plot(m$CustID, m$DateMatches - ExpectedDateMatches, type="l")
plot(m$CustID, m$SpendMatches - ExpectedSpendMatches, type="l")









