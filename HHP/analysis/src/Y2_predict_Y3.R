
# Use Y2 as a predictor of Y3 DIH values 

# First, define RMSLE error function & log1p functions
err <- function(p,a) { sqrt(mean((log(p+1)-log(a+1))^2)) }
log1p <- function(x) { log(x+1) } 
exp1m <- function(x) { exp(x)-1 } 

# Read data...
DaysInHospital.Y2 <- read.csv("hhp2data/DaysInHospital_Y2.csv")
DaysInHospital.Y3 <- read.csv("hhp2data/DaysInHospital_Y3.csv")

commonIDs <- intersect(DaysInHospital.Y2$MemberID, DaysInHospital.Y3$MemberID)

Y2.mean <- exp1m(mean(log1p(DaysInHospital.Y2$DaysInHospital)))
print(paste("Y2 mean DIH:", as.character(Y2.mean)))

# for ID's shared between Y2 & Y3, make Y2 DIH the prediction for Y3,
# otherwise default to the Y2 mean (when a Y3 ID not in Y2, so no info)
Y3.pred.DIH <- Y2.mean + 0*(DaysInHospital.Y3$DaysInHospital) #default to Y2 mean
err(DaysInHospital.Y3$DaysInHospital, Y3.pred.DIH) # error of just mean

ix3 <- match(commonIDs, DaysInHospital.Y3$MemberID) # find indexes of of commonIDs in Y3
ix2 <- match(commonIDs, DaysInHospital.Y2$MemberID) # ...and in Y2
Y3.pred.DIH[ix3] <- DaysInHospital.Y2$DaysInHospital[ix2] # copy Y2 DIH to Y3 
err(DaysInHospital.Y3$DaysInHospital, Y3.pred.DIH) # error when using Y2 to predict Y3

DIH.target <- DaysInHospital.Y3$DaysInHospital
logDIH.target <- log1p(DIH.target)
logDIH.pred   <- log1p(Y3.pred.DIH)
model   <- lm(logDIH.target ~ logDIH.pred ) 
print(model)
DIH.pred <- exp1m( predict(model) ) 
err(DIH.pred, DIH.target)

# Conclusion:  a predictor of exp1m(Y2DIH*0.2032 + 0.14) seems to give about RMSLE 0.466 on Y3

