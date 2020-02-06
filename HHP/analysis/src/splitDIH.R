# Heritage Health Prize
# Split DaysInHospital into two groups, 1 above a threshold, another below.
# For group above & below, predict the avg of that group (actually, exp(log(mean(x+1))))
# Once optimum split found, can use this info to create a binary classifier, rather than a regression
# by Chris Hefele

DATA_PATH <- "/home/chefele/HHP/download/HHP_release3/"
dih3 <- read.csv(paste(DATA_PATH,"DaysInHospital_Y3.csv",sep=""))
dih2 <- read.csv(paste(DATA_PATH,"DaysInHospital_Y2.csv",sep=""))

eps.score       <- function(p,a) { sqrt(mean((log(p+1)-log(a+1))^2)) }
mean.prediction <- function(x)   { exp( mean( log(x+1)))-1 } 

print.scores    <- function(dih) {
    for(THRESH in 0:14) {
        mask  <- dih$DaysInHospital > THRESH
        mean.above <- mean.prediction( dih$DaysInHospital[ mask] )
        mean.below <- mean.prediction( dih$DaysInHospital[!mask] )

        preds <- dih$DaysInHospital * 0 
        preds[ mask] <- mean.above 
        preds[!mask] <- mean.below

        split.score <- eps.score(preds, dih$DaysInHospital)
        print( paste(
                "Threshold:", as.character(THRESH),
                "Score:", as.character(split.score), 
                "AboveThreshMean:", as.character(mean.above),
                "BelowOrEqualThreshMean:", as.character(mean.below)
               )
             )
    }
}

cat("\n")
print.scores(dih2)
cat("\n")
print.scores(dih3)


